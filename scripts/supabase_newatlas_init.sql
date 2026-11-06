-- ==============================================================================
-- ACUATLAS 3D PRO / VI AN Y QUÁN - SUPABASE DATABASE INITIALIZATION SCRIPT
-- Dự án: Newatlas (https://zlhzlnpfrjngrzfccaoq.supabase.co)
-- Hỗ trợ: Đăng ký / Đăng nhập, Hồ sơ hội viên VIP, Đơn hàng nâng cấp VietQR,
--        Chính sách kiểm soát 03 Thiết bị (Device Management) & Realtime Admin
-- ==============================================================================

-- 1. BẢNG PROFILES (HỒ SƠ NGƯỜI DÙNG & HỘI VIÊN)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT DEFAULT '',
    role TEXT DEFAULT 'user', -- 'user' | 'admin'
    tier TEXT DEFAULT 'free', -- 'free' | 'annual' | 'lifetime'
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Bật Row Level Security (RLS) cho profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Admins have full access to profiles"
    ON public.profiles FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND (role = 'admin' OR email = 'tiendat.trinh@gmail.com')
        )
    );

-- Trigger tự động tạo profile khi người dùng đăng ký qua Supabase Auth
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, role, tier, expires_at)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        CASE WHEN lower(NEW.email) = 'tiendat.trinh@gmail.com' THEN 'admin' ELSE 'user' END,
        CASE WHEN lower(NEW.email) = 'tiendat.trinh@gmail.com' THEN 'lifetime' ELSE 'free' END,
        NULL
    )
    ON CONFLICT (id) DO UPDATE
    SET email = EXCLUDED.email,
        full_name = COALESCE(EXCLUDED.full_name, profiles.full_name);
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- 2. BẢNG UPGRADE_REQUESTS (ĐƠN ĐẶT HÀNG & CHUYỂN KHOẢN VIETQR)
CREATE TABLE IF NOT EXISTS public.upgrade_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_code TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    user_email TEXT NOT NULL,
    user_full_name TEXT DEFAULT '',
    package_id TEXT NOT NULL, -- 'annual' | 'lifetime'
    package_name TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    transfer_content TEXT NOT NULL,
    transfer_note TEXT DEFAULT '',
    status TEXT DEFAULT 'pending', -- 'pending' | 'approved' | 'rejected'
    approved_at TIMESTAMPTZ,
    approved_package TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.upgrade_requests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own upgrade requests"
    ON public.upgrade_requests FOR SELECT
    USING (user_email = auth.jwt()->>'email' OR user_id = auth.uid());

CREATE POLICY "Users can create upgrade requests"
    ON public.upgrade_requests FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Admins have full access to upgrade requests"
    ON public.upgrade_requests FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND (role = 'admin' OR email = 'tiendat.trinh@gmail.com')
        )
    );


-- 3. BẢNG USER_DEVICES (QUẢN LÝ TỐI ĐA 03 THIẾT BỊ CÁ NHÂN)
CREATE TABLE IF NOT EXISTS public.user_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    user_email TEXT NOT NULL,
    device_id TEXT NOT NULL,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL, -- 'mobile' | 'tablet' | 'desktop'
    is_active BOOLEAN DEFAULT true,
    last_active TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (user_id, device_id)
);

ALTER TABLE public.user_devices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own devices"
    ON public.user_devices FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Admins have full access to devices"
    ON public.user_devices FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND (role = 'admin' OR email = 'tiendat.trinh@gmail.com')
        )
    );


-- ==============================================================================
-- 4. CÁC HÀM RPC (STORED PROCEDURES) ĐƯỢC ỨNG DỤNG CLIENT GỌI TRỰC TIẾP
-- ==============================================================================

-- A. Lấy thông tin Profile người dùng
CREATE OR REPLACE FUNCTION public.rpc_get_user_profile(p_email TEXT)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_profile RECORD;
BEGIN
    SELECT * INTO v_profile FROM public.profiles WHERE lower(email) = lower(p_email) LIMIT 1;
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;
    RETURN row_to_json(v_profile);
END;
$$;

-- B. Tạo yêu cầu nâng cấp VIP (Mã đơn hàng VietQR riêng)
CREATE OR REPLACE FUNCTION public.rpc_create_upgrade_request(
    p_user_email TEXT,
    p_package_id TEXT,
    p_transfer_note TEXT DEFAULT '',
    p_transfer_content TEXT DEFAULT ''
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user RECORD;
    v_order_code TEXT;
    v_package_name TEXT;
    v_amount NUMERIC;
    v_content TEXT;
    v_req RECORD;
BEGIN
    SELECT * INTO v_user FROM public.profiles WHERE lower(email) = lower(p_user_email) LIMIT 1;
    
    v_order_code := 'ATLAS' || upper(substr(md5(random()::text), 1, 6));
    
    IF p_package_id = 'annual' THEN
        v_package_name := 'Gói Hội Viên VIP 1 Năm';
        v_amount := 399000;
    ELSE
        v_package_name := 'Gói Chuyên Gia VIP Trọn Đời';
        v_amount := 799000;
    END IF;
    
    v_content := COALESCE(NULLIF(p_transfer_content, ''), v_order_code);

    INSERT INTO public.upgrade_requests (
        order_code,
        user_id,
        user_email,
        user_full_name,
        package_id,
        package_name,
        amount,
        transfer_content,
        transfer_note,
        status
    )
    VALUES (
        v_order_code,
        v_user.id,
        p_user_email,
        COALESCE(v_user.full_name, split_part(p_user_email, '@', 1)),
        p_package_id,
        v_package_name,
        v_amount,
        v_content,
        p_transfer_note,
        'pending'
    )
    RETURNING * INTO v_req;

    RETURN row_to_json(v_req);
END;
$$;

-- C. Lấy danh sách đơn hàng cho Quản Trị Viên (Admin)
CREATE OR REPLACE FUNCTION public.rpc_get_upgrade_requests(p_status TEXT DEFAULT 'all')
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_result json;
BEGIN
    IF p_status = 'pending' THEN
        SELECT json_agg(r ORDER BY r.created_at DESC) INTO v_result
        FROM public.upgrade_requests r
        WHERE r.status = 'pending';
    ELSE
        SELECT json_agg(r ORDER BY r.created_at DESC) INTO v_result
        FROM public.upgrade_requests r;
    END IF;

    RETURN COALESCE(v_result, '[]'::json);
END;
$$;

-- D. Duyệt đơn hàng 1-chạm (Dành cho Admin)
CREATE OR REPLACE FUNCTION public.rpc_approve_upgrade_request(
    p_request_id UUID,
    p_package_id TEXT,
    p_duration_days INT DEFAULT 0
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_req RECORD;
    v_user RECORD;
    v_expires_at TIMESTAMPTZ := NULL;
    v_pkg_name TEXT;
BEGIN
    SELECT * INTO v_req FROM public.upgrade_requests WHERE id = p_request_id LIMIT 1;
    IF NOT FOUND THEN
        RETURN json_build_object('success', false, 'message', 'Không tìm thấy đơn hàng');
    END IF;

    SELECT * INTO v_user FROM public.profiles WHERE lower(email) = lower(v_req.user_email) LIMIT 1;
    
    IF p_duration_days > 0 THEN
        IF v_user.expires_at IS NOT NULL AND v_user.expires_at > now() THEN
            v_expires_at := v_user.expires_at + (p_duration_days || ' days')::interval;
        ELSE
            v_expires_at := now() + (p_duration_days || ' days')::interval;
        END IF;
    ELSE
        v_expires_at := NULL;
    END IF;

    IF p_package_id = 'annual' THEN
        v_pkg_name := 'Gói Hội Viên VIP 1 Năm';
    ELSE
        v_pkg_name := 'Gói Chuyên Gia VIP Trọn Đời';
    END IF;

    UPDATE public.upgrade_requests
    SET status = 'approved',
        approved_at = now(),
        approved_package = v_pkg_name
    WHERE id = p_request_id;

    IF v_user.id IS NOT NULL THEN
        UPDATE public.profiles
        SET tier = p_package_id,
            expires_at = v_expires_at,
            updated_at = now()
        WHERE id = v_user.id;
    END IF;

    RETURN json_build_object(
        'success', true,
        'message', 'Đã kích hoạt ' || v_pkg_name,
        'expires_at', v_expires_at
    );
END;
$$;

-- E. Kích hoạt VIP thủ công qua Email (Dành cho Admin)
CREATE OR REPLACE FUNCTION public.rpc_manual_activate_user(
    p_email TEXT,
    p_package_id TEXT,
    p_duration_days INT DEFAULT 0
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user RECORD;
    v_expires_at TIMESTAMPTZ := NULL;
    v_pkg_name TEXT;
BEGIN
    SELECT * INTO v_user FROM public.profiles WHERE lower(email) = lower(p_email) LIMIT 1;

    IF p_duration_days > 0 THEN
        IF v_user.id IS NOT NULL AND v_user.expires_at IS NOT NULL AND v_user.expires_at > now() THEN
            v_expires_at := v_user.expires_at + (p_duration_days || ' days')::interval;
        ELSE
            v_expires_at := now() + (p_duration_days || ' days')::interval;
        END IF;
    ELSE
        v_expires_at := NULL;
    END IF;

    IF p_package_id = 'annual' THEN
        v_pkg_name := 'Gói Hội Viên VIP 1 Năm';
    ELSE
        v_pkg_name := 'Gói Chuyên Gia VIP Trọn Đời';
    END IF;

    IF v_user.id IS NOT NULL THEN
        UPDATE public.profiles
        SET tier = p_package_id,
            expires_at = v_expires_at,
            updated_at = now()
        WHERE id = v_user.id;
    END IF;

    RETURN json_build_object(
        'success', true,
        'message', 'Đã kích hoạt ' || v_pkg_name || ' cho ' || p_email,
        'expires_at', v_expires_at
    );
END;
$$;

-- F. Đăng ký thiết bị & Kiểm soát tối đa 03 thiết bị cá nhân
CREATE OR REPLACE FUNCTION public.rpc_register_device(
    p_device_id TEXT,
    p_device_name TEXT,
    p_device_type TEXT
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user_id UUID := auth.uid();
    v_user_email TEXT := auth.jwt()->>'email';
    v_active_count INT;
    v_oldest_device_id TEXT;
BEGIN
    IF v_user_id IS NULL THEN
        RETURN json_build_object('success', false, 'message', 'Chưa đăng nhập');
    END IF;

    -- Thêm hoặc cập nhật thiết bị hiện tại
    INSERT INTO public.user_devices (user_id, user_email, device_id, device_name, device_type, is_active, last_active)
    VALUES (v_user_id, v_user_email, p_device_id, p_device_name, p_device_type, true, now())
    ON CONFLICT (user_id, device_id) DO UPDATE
    SET device_name = EXCLUDED.device_name,
        device_type = EXCLUDED.device_type,
        is_active = true,
        last_active = now();

    -- Đếm số lượng thiết bị đang kích hoạt của tài khoản
    SELECT count(*) INTO v_active_count
    FROM public.user_devices
    WHERE user_id = v_user_id AND is_active = true;

    -- Nếu vượt quá 3 thiết bị -> tự động ngắt kết nối (evict) thiết bị cũ nhất
    IF v_active_count > 3 THEN
        SELECT device_id INTO v_oldest_device_id
        FROM public.user_devices
        WHERE user_id = v_user_id AND is_active = true AND device_id <> p_device_id
        ORDER BY last_active ASC
        LIMIT 1;

        IF v_oldest_device_id IS NOT NULL THEN
            UPDATE public.user_devices
            SET is_active = false
            WHERE user_id = v_user_id AND device_id = v_oldest_device_id;
        END IF;
    END IF;

    RETURN json_build_object('success', true, 'device_id', p_device_id);
END;
$$;

-- G. Kiểm tra tình trạng hoạt động của thiết bị hiện tại
CREATE OR REPLACE FUNCTION public.rpc_check_device_status(p_device_id TEXT)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user_id UUID := auth.uid();
    v_device RECORD;
BEGIN
    IF v_user_id IS NULL THEN
        RETURN json_build_object('is_active', true, 'is_vip', false);
    END IF;

    SELECT * INTO v_device
    FROM public.user_devices
    WHERE user_id = v_user_id AND device_id = p_device_id
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN json_build_object('is_active', true);
    END IF;

    IF v_device.is_active = true THEN
        UPDATE public.user_devices SET last_active = now() WHERE id = v_device.id;
    END IF;

    RETURN json_build_object('is_active', v_device.is_active, 'device_name', v_device.device_name);
END;
$$;

-- H. Hủy quyền thiết bị (Đăng xuất khỏi thiết bị)
CREATE OR REPLACE FUNCTION public.rpc_revoke_device(p_device_id TEXT)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user_id UUID := auth.uid();
BEGIN
    UPDATE public.user_devices
    SET is_active = false
    WHERE user_id = v_user_id AND device_id = p_device_id;

    RETURN json_build_object('success', true);
END;
$$;

-- I. Lấy danh sách các thiết bị của người dùng
CREATE OR REPLACE FUNCTION public.rpc_get_user_devices()
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user_id UUID := auth.uid();
    v_result json;
BEGIN
    SELECT json_agg(d ORDER BY d.last_active DESC) INTO v_result
    FROM public.user_devices d
    WHERE d.user_id = v_user_id;

    RETURN COALESCE(v_result, '[]'::json);
END;
$$;

-- Kích hoạt tính năng Realtime cho bảng upgrade_requests & profiles để Admin nhận đơn tức thì
ALTER PUBLICATION supabase_realtime ADD TABLE public.upgrade_requests;
ALTER PUBLICATION supabase_realtime ADD TABLE public.profiles;

