import re

# ==========================================
# 1. UPDATE web/js/dissectionStudio.js
# ==========================================
with open('web/js/dissectionStudio.js', 'r', encoding='utf-8') as f:
    studio = f.read()

# Add getNerveInfo method to DissectionStudio class
get_nerve_info_js = """  getNerveInfo(raw) {
    const s = (raw || '').trim();
    const norm = s.replace(/[\\(\\)\\.\\d]/g, '').toLowerCase();
    let vi = 'Dây thần kinh ' + s.replace(/CU|OB|_/g, ' ').trim();
    let lat = s;
    let roots = 'Xuất phát từ rễ thần kinh gai sống hoặc thần kinh sọ tương ứng.';
    let func = 'Dẫn truyền xung động cảm giác và vận động chi phối cơ quan đích.';
    let acupoints = 'Hệ thống thần kinh phân bố tương ứng với đường kinh lạc và các huyệt vị tiết đoạn.';
    let note = 'Cấu trúc dẫn truyền thần kinh Z-Anatomy.';

    if (norm.includes('sciatic')) {
      vi = 'Thần kinh hông to (Thần kinh tọa)';
      lat = 'Nervus ischiadicus';
      roots = 'Rễ gai sống L4, L5, S1, S2, S3 (Đám rối cùng)';
      func = 'Dây thần kinh lớn nhất và dài nhất cơ thể; chi phối vận động nhóm cơ đùi sau và toàn bộ cẳng chân, bàn chân.';
      acupoints = 'Chui dưới cơ hình lê: Hoàn Khiêu (GB30), Trật Biên (BL54), Ân Môn (BL37), Ủy Trung (BL40 - Hợp huyệt kinh Bàng Quang).';
      note = 'Thường bị chèn ép do thoát vị đĩa đệm L4-L5, L5-S1 hoặc hội chứng cơ hình lê gây đau thần kinh tọa.';
    } else if (norm.includes('femoral')) {
      vi = 'Dây thần kinh đùi';
      lat = 'Nervus femoralis';
      roots = 'Rễ gai sống L2, L3, L4 (Đám rối thắt lưng)';
      func = 'Chi phối vận động cơ tứ đầu đùi, cơ may; cảm giác mặt trước đùi và bờ trong cẳng chân.';
      acupoints = 'Chui dưới dây chằng bẹn: Khí Xung (ST30), Xung Môn (SP12), Bễ Quan (ST31), Phục Thỏ (ST32), Lương Khâu (ST34).';
      note = 'Tổn thương gây mất phản xạ gân bánh chè, teo cơ tứ đầu đùi.';
    } else if (norm.includes('radial')) {
      vi = 'Dây thần kinh quay';
      lat = 'Nervus radialis';
      roots = 'Rễ gai sống C5, C6, C7, C8, T1';
      func = 'Chi phối toàn bộ cơ duỗi cẳng tay, cổ tay và ngón tay; cảm giác mặt sau cánh tay và nửa ngoài mu tay.';
      acupoints = 'Chạy trong rãnh xoắn xương cánh tay: Khúc Trì (LI11), Thủ Tam Lý (LI10), Hợp Cốc (LI4), Dương Khê (LI5).';
      note = 'Liệt thần kinh quay gây dấu hiệu bàn tay rũ cổ cò, mất khả năng duỗi cổ tay.';
    } else if (norm.includes('median')) {
      vi = 'Dây thần kinh giữa';
      lat = 'Nervus medianus';
      roots = 'Rễ gai sống C6, C7, C8, T1';
      func = 'Chi phối các cơ gấp cẳng tay trước, cơ ô mô cái; cảm giác gan tay 3 ngón rưỡi ngoài.';
      acupoints = 'Chui qua ống cổ tay: Khúc Trạch (PC3), Gian Sử (PC5), Nội Quan (PC6), Đại Lăng (PC7), Lao Cung (PC8).';
      note = 'Hội chứng ống cổ tay gây tê bì 3 ngón rưỡi ngoài, teo mô cái hình bàn tay khỉ.';
    } else if (norm.includes('ulnar')) {
      vi = 'Dây thần kinh trụ';
      lat = 'Nervus ulnaris';
      roots = 'Rễ gai sống C8, T1';
      func = 'Chi phối cơ ô mô út, cơ gian cốt; cảm giác 1 ngón rưỡi trong.';
      acupoints = 'Đi qua rãnh ròng rọc khuỷu tay: Tiểu Hải (SI8), Chi Chánh (SI7), Thần Môn (HT7), Thiếu Phủ (HT8).';
      note = 'Tổn thương gây biến dạng bàn tay vuốt trụ (Claw hand).';
    } else if (norm.includes('tibial')) {
      vi = 'Dây thần kinh chày';
      lat = 'Nervus tibialis';
      roots = 'Rễ gai sống L4, L5, S1, S2, S3';
      func = 'Chi phối toàn bộ cơ bắp chân sau và các cơ gan chân; cảm giác toàn bộ gan bàn chân.';
      acupoints = 'Đi dọc bắp chân sau: Ủy Trung (BL40), Hợp Dương (BL55), Thừa Sơn (BL57), Thái Khê (KI3), Dũng Tuyền (KI1).';
      note = 'Tổn thương làm mất động tác gấp bàn chân về phía gan chân.';
    } else if (norm.includes('fibular') || norm.includes('peroneal')) {
      const isDeep = norm.includes('deep');
      const isSuper = norm.includes('superficial');
      const sub = isDeep ? ' sâu' : (isSuper ? ' nông' : ' chung');
      vi = 'Thần kinh mác' + sub;
      lat = 'Nervus fibularis (peroneus)';
      roots = 'Rễ gai sống L4, L5, S1, S2';
      func = 'Chi phối các cơ cẳng chân trước và ngoài; vận động gấp mu chân và nghiêng ngoài.';
      acupoints = 'Vòng quanh chỏm xương mác: Dương Lăng Tuyền (GB34), Huyền Chung (GB39), Túc Tam Lý (ST36), Giải Khê (ST41).';
      note = 'Liệt thần kinh mác chung gây dáng đi gà, bàn chân rũ.';
    } else if (norm.includes('intercostal')) {
      vi = 'Dây thần kinh gian sườn';
      lat = 'Nervus intercostalis';
      roots = 'Rễ gai sống ngực T1 - T11';
      func = 'Chạy trong rãnh sườn ở bờ dưới các xương sườn; chi phối vận động cơ gian sườn và cảm giác thành ngực bụng.';
      acupoints = 'Huyệt Hoa Đà Giáp Ất (EX-B2), Du huyệt kinh Bàng Quang, Kỳ Môn (LR14), Nhật Nguyệt (GB24), Chương Môn (LR13).';
      note = 'Đau dây thần kinh liên sườn thường gặp sau nhiễm virus Zona hoặc thoái hóa cột sống ngực.';
    } else if (norm.includes('vagus')) {
      vi = 'Dây thần kinh phế vị (Thần kinh sọ X)';
      lat = 'Nervus vagus (CN X)';
      roots = 'Hành não, chui qua lỗ tĩnh mạch cảnh';
      func = 'Dây đối giao cảm lớn nhất: chậm nhịp tim, co thắt phế quản, tăng tiết dịch và nhu động tiêu hóa.';
      acupoints = 'Thiên Đột (CV22), Nhân Nghênh (ST9), Nội Quan (PC6), Trung Quản (CV12).';
      note = 'Dây thần kinh tự chủ sống còn chi phối phần lớn các tạng lồng ngực và ổ bụng.';
    } else if (norm.includes('phrenic')) {
      vi = 'Dây thần kinh hoành';
      lat = 'Nervus phrenicus';
      roots = 'Rễ gai sống cổ C3, C4, C5 (chủ yếu là C4)';
      func = 'Dây thần kinh duy nhất chi phối vận động toàn bộ cơ hoành (cơ hô hấp chính).';
      acupoints = 'Khuyết Bồn (ST12), Thiên Đột (CV22), Cự Khuyết (CV14).';
      note = 'Liệt thần kinh hoành gây khó thở nghiêm trọng và liệt vòm hoành cùng bên.';
    } else if (norm.includes('facial')) {
      vi = 'Dây thần kinh mặt (Thần kinh sọ VII)';
      lat = 'Nervus facialis (CN VII)';
      roots = 'Rãnh hành - cầu não, chui ra ở lỗ trâm chũm';
      func = 'Chi phối vận động toàn bộ cơ biểu cảm nét mặt, vị giác 2/3 trước lưỡi.';
      acupoints = 'Ế Phong (TE17 - nơi thoát ra lỗ trâm chũm), Địa Thương (ST4), Giáp Xa (ST6), Hạ Quan (ST7), Tứ Bạch (ST2).';
      note = 'Liệt mặt ngoại biên Bell\'s palsy: méo miệng, mắt nhắm không kín (Charles Bell).';
    } else if (norm.includes('trigeminal') || norm.includes('mandibular') || norm.includes('maxillary') || norm.includes('ophthalmic')) {
      vi = 'Dây thần kinh sinh ba (Thần kinh sọ V)';
      lat = 'Nervus trigeminus (CN V)';
      roots = 'Mặt trước bên cầu não, tạo hạch Gasser';
      func = 'Cảm giác chính vùng mặt, răng miệng và vận động cơ nhai.';
      acupoints = 'Toản Trúc (BL2), Tứ Bạch (ST2), Thừa Tương (CV24), Hạ Quan (ST7).';
      note = 'Cơn đau dây thần kinh số V đau dữ dội như điện giật.';
    } else if (norm.includes('plexus')) {
      const pType = norm.includes('brachial') ? 'cánh tay' : (norm.includes('lumbar') ? 'thắt lưng' : (norm.includes('sacral') ? 'cùng' : 'thần kinh'));
      vi = 'Đám rối thần kinh ' + pType;
      roots = 'Hội tụ các rễ trước của các dây thần kinh gai sống tương ứng.';
      func = 'Mạng lưới phân nhánh tạo các dây thần kinh chính chi phối chi và thân thể.';
      acupoints = 'Cực Tuyền (HT1), Kiên Tỉnh (GB21), Đại Trường Du (BL25), Bát Liêu (BL31-BL34).';
      note = 'Mạng lưới phân phối thần kinh quan trọng.';
    } else if (norm.includes('spinal') || norm.includes('cord')) {
      vi = 'Tủy sống & Thần kinh gai sống';
      lat = 'Medulla spinalis';
      roots = '31 đôi dây thần kinh gai sống';
      func = 'Trung tâm phản xạ và đường dẫn truyền cảm giác - vận động chính giữa não và toàn thân.';
      acupoints = 'Mạch Đốc: Đại Chùy (GV14), Mệnh Môn (GV4); Chuỗi huyệt Hoa Đà Giáp Ất (EX-B2).';
      note = 'Trung khu phản xạ tủy và dẫn truyền thần kinh trung ương.';
    }

    return { vi, lat, roots, func, acupoints, note };
  }
"""

if 'getNerveInfo(raw)' not in studio:
    pos_helpers = studio.find('getVesselInfo(raw)')
    if pos_helpers != -1:
        studio = studio[:pos_helpers] + get_nerve_info_js + "\n" + studio[pos_helpers:]
        print("Studio: Added getNerveInfo method")

# Update this.nervesModel.traverse in studio to use getNerveInfo
old_nerve_traverse = """          const mName = child.name || '';
          let match = Object.keys(nerveDictionary).find(k => mName.includes(k));
          let vi = 'Dây thần kinh gai sống / Gian sườn';
          let lat = 'Nervus spinalis / intercostalis';
          let note = 'Chi phối cảm giác và vận động phân đoạn (Huyệt Hoa Đà Giáp Ất EX-B2 & Du huyệt BL).';

          if (match) {
            vi = nerveDictionary[match].vi;
            lat = nerveDictionary[match].lat;
            note = nerveDictionary[match].note;
          } else if (mName.includes('brachial')) {
            vi = 'Đám rối thần kinh cánh tay';
            lat = 'Plexus brachialis';
            note = 'Hội tụ từ rễ C5-T1 chui qua hố nách (Huyệt Cực Tuyền HT1).';
          } else if (mName.includes('intercostal')) {
            vi = 'Dây thần kinh gian sườn';
            lat = 'Nervus intercostalis';
            note = 'Men theo bờ dưới xương sườn ra thành ngực bụng (Kỳ Môn LR14, Nhật Nguyệt GB24, Chương Môn LR13).';
          }

          child.userData = {
            isNerve: true,
            meshName: mName,
            nameVi: vi,
            nameLat: lat,
            note: note,
            layer: 'nerves'
          };"""

new_nerve_traverse = """          const mName = child.name || '';
          const nInfo = this.getNerveInfo(mName);
          child.userData = {
            isNerve: true,
            meshName: mName,
            nameVi: nInfo.vi,
            nameLat: nInfo.lat,
            roots: nInfo.roots,
            function: nInfo.func,
            acupoints: nInfo.acupoints,
            note: nInfo.note,
            layer: 'nerves'
          };"""

if old_nerve_traverse in studio:
    studio = studio.replace(old_nerve_traverse, new_nerve_traverse, 1)
    print("Studio: Updated nervesModel traversal with getNerveInfo")
else:
    print("WARNING: old_nerve_traverse not found in studio")

# Update getActiveCandidateMeshes in studio to auto-init vessels and lymphatic
old_active_cand = """  getActiveCandidateMeshes() {
    const all = [
      ...this.allMuscles,
      ...this.bones,
      ...this.organs,
      ...this.nerves,
      ...this.vessels,
      ...this.lymphatic
    ];
    return all.filter(m => this.isMeshActuallyVisible(m) && !this.peeledObjects.has(m));
  }"""

new_active_cand = """  getActiveCandidateMeshes() {
    if (window.vesselsModel && (!this.vessels || !this.vessels.length)) {
      this.initVesselsModel(window.vesselsModel);
    }
    if (window.lymphaticModel && (!this.lymphatic || !this.lymphatic.length)) {
      this.initLymphaticModel(window.lymphaticModel);
    }
    const all = [
      ...this.allMuscles,
      ...this.bones,
      ...this.organs,
      ...this.nerves,
      ...this.vessels,
      ...this.lymphatic
    ];
    return all.filter(m => this.isMeshActuallyVisible(m) && !this.peeledObjects.has(m));
  }"""

if old_active_cand in studio:
    studio = studio.replace(old_active_cand, new_active_cand, 1)
    print("Studio: Updated getActiveCandidateMeshes with auto-init")
else:
    print("WARNING: old_active_cand not found in studio")

with open('web/js/dissectionStudio.js', 'w', encoding='utf-8') as f:
    f.write(studio)

print("Saved web/js/dissectionStudio.js!")
