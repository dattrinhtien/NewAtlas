/**
 * storageManager.js
 * Quản lý Caching cục bộ các tệp mô hình giải phẫu 3D dung lượng lớn (GLB)
 * bằng IndexedDB phía Client + Persistent Storage API.
 *
 * Tiêu chí:
 * - Khi bật một hệ giải phẫu mới: Kiểm tra trong máy trước.
 * - Nếu có: Trả về ArrayBuffer tức thì (< 0.1s), không tốn dữ liệu mạng.
 * - Nếu đang được tiến trình ngầm (Background Preloader) tải dở: Gắn chung vào tiến trình đó, không tải trùng lặp.
 * - Nếu chưa có: Tải nhị phân theo stream với thanh tiến trình %, lưu vĩnh viễn vào IndexedDB.
 */

class AnatomyStorageManager {
  constructor() {
    this.dbName = 'NewAtlas_AnatomyCache';
    this.storeName = 'model_blobs';
    this.metaStoreName = 'model_metadata';
    this.dbVersion = 1;
    this.db = null;
    this.inflightPromises = new Map();
    this.progressSubscribers = new Map();
    this.persistRequested = false;
  }

  async requestPersistentStorage() {
    if (this.persistRequested) return;
    this.persistRequested = true;
    try {
      if (navigator.storage && navigator.storage.persist) {
        const isPersisted = await navigator.storage.persisted();
        if (!isPersisted) {
          await navigator.storage.persist();
        }
      }
    } catch (e) {
      // Ignore on unsupported browsers
    }
  }

  async init() {
    if (this.db) return this.db;
    this.requestPersistentStorage();
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName);
        }
        if (!db.objectStoreNames.contains(this.metaStoreName)) {
          db.createObjectStore(this.metaStoreName, { keyPath: 'id' });
        }
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        resolve(this.db);
      };

      request.onerror = (event) => {
        console.error('[StorageManager] Lỗi mở IndexedDB:', event.target.error);
        reject(event.target.error);
      };
    });
  }

  async isCached(systemId) {
    if (!this.db) await this.init();
    return new Promise((resolve) => {
      try {
        const transaction = this.db.transaction([this.metaStoreName, this.storeName], 'readonly');
        const metaStore = transaction.objectStore(this.metaStoreName);
        const metaReq = metaStore.get(systemId);
        metaReq.onsuccess = () => {
          if (metaReq.result && metaReq.result.sizeBytes > 0) {
            resolve(true);
          } else {
            const store = transaction.objectStore(this.storeName);
            const req = store.getKey ? store.getKey(systemId) : store.get(systemId);
            req.onsuccess = () => resolve(!!req.result);
            req.onerror = () => resolve(false);
          }
        };
        metaReq.onerror = () => resolve(false);
      } catch (e) {
        resolve(false);
      }
    });
  }

  async getFromCache(systemId) {
    if (!this.db) await this.init();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.get(systemId);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = (e) => reject(e);
    });
  }

  async saveToCache(systemId, arrayBuffer, sizeBytes) {
    if (!this.db) await this.init();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName, this.metaStoreName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const metaStore = transaction.objectStore(this.metaStoreName);

      store.put(arrayBuffer, systemId);
      metaStore.put({
        id: systemId,
        sizeBytes: sizeBytes || arrayBuffer.byteLength,
        savedAt: new Date().toISOString()
      });

      transaction.oncomplete = () => resolve(true);
      transaction.onerror = (e) => reject(e);
    });
  }

  /**
   * Tải hệ giải phẫu với chiến lược Cache-First & In-flight Deduplication:
   * - Nếu đã lưu trong máy -> Đọc tức thì (< 0.1s).
   * - Nếu đang được tải ngầm -> Gắn thêm callback onProgress và dùng chung Promise đang tải.
   * - Nếu chưa -> Fetch với callback onProgress(percent, loadedBytes, totalBytes), rồi lưu vào máy.
   */
  async loadSystemData(systemId, url, onProgress) {
    if (!this.db) await this.init();

    // 1. Kiểm tra cache trước
    const cachedBuffer = await this.getFromCache(systemId);
    if (cachedBuffer) {
      if (onProgress) onProgress(100, cachedBuffer.byteLength, cachedBuffer.byteLength, true);
      return { data: cachedBuffer, isCached: true };
    }

    // 2. Nếu tệp này đang được tải ngầm (hoặc tải từ thao tác khác), gắn chung vào Promise đang chạy
    if (this.inflightPromises.has(systemId)) {
      if (onProgress) {
        const subs = this.progressSubscribers.get(systemId) || [];
        subs.push(onProgress);
        this.progressSubscribers.set(systemId, subs);
      }
      return this.inflightPromises.get(systemId);
    }

    // 3. Khởi tạo lượt tải mới qua mạng
    const subs = [];
    if (onProgress) subs.push(onProgress);
    this.progressSubscribers.set(systemId, subs);

    const notifyProgress = (percent, loaded, total, cached) => {
      const list = this.progressSubscribers.get(systemId) || [];
      for (const fn of list) {
        try {
          fn(percent, loaded, total, cached);
        } catch (e) {
          // ignore callback error
        }
      }
    };

    const downloadPromise = (async () => {
      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Không thể tải tệp ${url}: ${response.status} ${response.statusText}`);
        }

        const contentLength = +response.headers.get('Content-Length') || 0;
        let arrayBuffer;
        let receivedLength = 0;

        if (response.body) {
          const reader = response.body.getReader();
          const chunks = [];

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
            receivedLength += value.length;

            if (contentLength > 0) {
              const percent = Math.min(100, Math.round((receivedLength / contentLength) * 100));
              notifyProgress(percent, receivedLength, contentLength, false);
            } else {
              notifyProgress(null, receivedLength, 0, false);
            }
          }

          const fullBlob = new Blob(chunks);
          arrayBuffer = await fullBlob.arrayBuffer();
        } else {
          arrayBuffer = await response.arrayBuffer();
          receivedLength = arrayBuffer.byteLength;
        }

        notifyProgress(100, receivedLength, receivedLength, false);

        // Lưu vào IndexedDB cho các lần truy cập tiếp theo
        try {
          await this.saveToCache(systemId, arrayBuffer, receivedLength);
        } catch (err) {
          console.warn('[StorageManager] Không thể lưu vào IndexedDB:', err);
        }

        return { data: arrayBuffer, isCached: false };
      } finally {
        this.inflightPromises.delete(systemId);
        this.progressSubscribers.delete(systemId);
      }
    })();

    this.inflightPromises.set(systemId, downloadPromise);
    return downloadPromise;
  }

  /**
   * Tính toán tổng dung lượng đã lưu trong máy
   */
  async getStorageStats() {
    if (!this.db) await this.init();
    return new Promise((resolve) => {
      const transaction = this.db.transaction([this.metaStoreName], 'readonly');
      const store = transaction.objectStore(this.metaStoreName);
      const request = store.getAll();

      request.onsuccess = () => {
        const items = request.result || [];
        let totalBytes = 0;
        const details = {};
        for (const it of items) {
          totalBytes += it.sizeBytes || 0;
          details[it.id] = it;
        }
        resolve({
          count: items.length,
          totalBytes,
          totalMB: (totalBytes / (1024 * 1024)).toFixed(1),
          details
        });
      };
      request.onerror = () => resolve({ count: 0, totalBytes: 0, totalMB: '0.0', details: {} });
    });
  }

  /**
   * Xóa toàn bộ cache để giải phóng bộ nhớ
   */
  async clearAllCache() {
    if (!this.db) await this.init();
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName, this.metaStoreName], 'readwrite');
      transaction.objectStore(this.storeName).clear();
      transaction.objectStore(this.metaStoreName).clear();
      transaction.oncomplete = () => resolve(true);
      transaction.onerror = (e) => reject(e);
    });
  }
}

export const storageManager = new AnatomyStorageManager();
window.anatomyStorageManager = storageManager;
