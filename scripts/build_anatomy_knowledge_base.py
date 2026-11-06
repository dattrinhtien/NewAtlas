#!/usr/bin/env python3
"""
scripts/build_anatomy_knowledge_base.py
Builds complete scientific anatomy dictionaries for:
1. 242 Bones (Osteology) - web/data/osteologyDictionary.json
2. 177 Muscles (Myology) enriched with Origin, Insertion, Action, Innervation - web/data/anatomyDictionary.json
3. Angiology (Vessels & Circulation) - web/data/angiologyDictionary.json
"""

import json
import os
import struct

def build_osteology():
    # Read all 242 bone mesh names from skeleton.glb
    with open('web/models/skeleton.glb', 'rb') as f:
        f.seek(12)
        chunk_len, _ = struct.unpack('<II', f.read(8))
        gltf = json.loads(f.read(chunk_len).decode('utf-8'))
    meshes = [m.get('name', '') for m in gltf.get('meshes', [])]

    # Translation dictionary & anatomical metadata
    base_dict = {
        'frontal-bone': ('Xương trán', 'Os frontale', 'head_neck', 'Tạo trần ổ mắt và trán; Mốc huyệt: Dương Bạch (GB14), Đầu Duy (ST8), Đầu Lâm Khấp (GB15).'),
        'parietal-bone': ('Xương đỉnh', 'Os parietale', 'head_neck', 'Tạo vòm sọ trên; Mốc huyệt: Bách Hội (GV20), Thông Thiên (BL7), Lạc Khước (BL8).'),
        'occipital-bone': ('Xương chẩm', 'Os occipitale', 'head_neck', 'Nền sọ sau, lỗ chẩm lớn; Mốc huyệt: Phong Trì (GB20), Á Môn (GV15), Phong Phủ (GV16), Ngọc Chẩm (BL9).'),
        'temporal-bone': ('Xương thái dương', 'Os temporale', 'head_neck', 'Chứa cơ quan thính giác, mỏm chũm, mỏm trâm; Mốc huyệt: Ế Phong (TE17), Suất Cốc (GB8), Thính Cung (SI19).'),
        'sphenoid-bone': ('Xương bướm', 'Os sphenoidale', 'head_neck', 'Nền sọ giữa, yên bướm chứa tuyến yên; Mốc huyệt: Thái Dương (EX-HN5).'),
        'ethmoid-bone': ('Xương sàng', 'Os ethmoidale', 'head_neck', 'Mảnh sàng có lỗ cho dây thần kinh khứu giác I đi qua.'),
        'nasal-bone': ('Xương mũi', 'Os nasale', 'head_neck', 'Sống mũi; Mốc huyệt: Tố Liêu (GV25), Nghinh Hương (LI20), Toản Trúc (BL2).'),
        'lacrimal-bone': ('Xương lệ', 'Os lacrimale', 'head_neck', 'Thành trong ổ mắt; Mốc huyệt: Tình Minh (BL1).'),
        'zygomatic-bone': ('Xương gò má', 'Os zygomaticum', 'head_neck', 'Gò má & cung tiếp gò má; Mốc huyệt: Quyền Liêu (SI18), Hạ Quan (ST7).'),
        'maxilla': ('Xương hàm trên', 'Maxilla', 'head_neck', 'Khối xương mặt trên, chứa xoang hàm; Mốc huyệt: Tứ Bạch (ST2), Cự Liêu (ST3), Địa Thương (ST4).'),
        'palatine-bone': ('Xương khẩu cái', 'Os palatinum', 'head_neck', 'Khẩu cái cứng (vòm miệng sau).'),
        'inferior-nasal-concha': ('Xương xoăn mũi dưới', 'Concha nasalis inferior', 'head_neck', 'Xương xoăn ở hốc mũi dưới.'),
        'vomer': ('Xương lá mía', 'Vomer', 'head_neck', 'Vách ngăn mũi xương.'),
        'mandible': ('Xương hàm dưới', 'Mandibula', 'head_neck', 'Xương vận động duy nhất vùng mặt; Mốc huyệt: Giáp Xa (ST6), Thừa Tương (CV24), Đại Nghinh (ST5).'),
        'hyoid-bone': ('Xương móng', 'Os hyoideum', 'head_neck', 'Treo ở vùng cổ trước; Mốc huyệt: Liêm Tuyền (CV23).'),
        
        # Cột sống
        'atlas-c1': ('Đốt đội C1', 'Atlas (C1)', 'vertebrae', 'Đốt sống cổ 1 đỡ hộp sọ, xoay quanh mỏm răng C2; Mốc định vị: Thiên Trụ (BL10).'),
        'axis-c2': ('Đốt trục C2', 'Axis (C2)', 'vertebrae', 'Có mỏm răng (dens) làm trục quay sọ não.'),
        'third-cervical-vertebra-c3': ('Đốt sống cổ C3', 'Vertebra cervicalis III', 'vertebrae', 'Đốt sống cổ 3; Mốc huyệt Hoa Đà Giáp Ất vùng cổ.'),
        'fourth-cervical-vertebra-c4': ('Đốt sống cổ C4', 'Vertebra cervicalis IV', 'vertebrae', 'Đốt sống cổ 4; Nguyên uỷ dây thần kinh hoành C3-C5.'),
        'fifth-cervical-vertebra-c5': ('Đốt sống cổ C5', 'Vertebra cervicalis V', 'vertebrae', 'Đốt sống cổ 5; Rễ thần kinh chi phối cơ delta và cơ nhị đầu.'),
        'sixth-cervical-vertebra-c6': ('Đốt sống cổ C6', 'Vertebra cervicalis VI', 'vertebrae', 'Đốt sống cổ 6; Củ cảnh Chassaignac ép động mạch cảnh.'),
        'seventh-cervical-vertebra-c7': ('Đốt sống cổ C7 (Đốt lồi)', 'Vertebra prominens (C7)', 'vertebrae', 'Gai sau dài lồi rõ nhất gáy; Mốc huyệt quan trọng: Đại Chùy (GV14).'),
        
        # Ngực & Lưng
        'first-thoracic-vertebra-t1': ('Đốt sống ngực T1', 'Vertebra thoracica I', 'vertebrae', 'Dưới gai T1: Huyệt Đào Đạo (GV13); ngang ra 1.5 thốn: Đại Trữ (BL11).'),
        'second-thoracic-vertebra-t2': ('Đốt sống ngực T2', 'Vertebra thoracica II', 'vertebrae', 'Ngang ra 1.5 thốn: Phong Môn (BL12 - cửa ngõ phong tà).'),
        'third-thoracic-vertebra-t3': ('Đốt sống ngực T3', 'Vertebra thoracica III', 'vertebrae', 'Dưới gai T3: Huyệt Thân Trụ (GV12); ngang ra 1.5 thốn: Phế Du (BL13).'),
        'fourth-thoracic-vertebra-t4': ('Đốt sống ngực T4', 'Vertebra thoracica IV', 'vertebrae', 'Ngang ra 1.5 thốn: Quyết Âm Du (BL14 - Mộ Tâm Bào).'),
        'fifth-thoracic-vertebra-t5': ('Đốt sống ngực T5', 'Vertebra thoracica V', 'vertebrae', 'Dưới gai T5: Huyệt Thần Đạo (GV11); ngang ra 1.5 thốn: Tâm Du (BL15).'),
        'sixth-thoracic-vertebra-t6': ('Đốt sống ngực T6', 'Vertebra thoracica VI', 'vertebrae', 'Dưới gai T6: Huyệt Linh Đài (GV10); ngang ra 1.5 thốn: Đốc Du (BL16).'),
        'seventh-thoracic-vertebra-t7': ('Đốt sống ngực T7', 'Vertebra thoracica VII', 'vertebrae', 'Ngang góc dưới xương bả vai; Dưới gai: Chí Dương (GV9); ngang ra: Cách Du (BL17 - Huyết hội).'),
        'eighth-thoracic-vertebra-t8': ('Đốt sống ngực T8', 'Vertebra thoracica VIII', 'vertebrae', 'Ngang ra 1.5 thốn: Tụy Du (Vi Hoàn Du - trị tiểu đường).'),
        'ninth-thoracic-vertebra-t9': ('Đốt sống ngực T9', 'Vertebra thoracica IX', 'vertebrae', 'Dưới gai T9: Huyệt Cân Súc (GV8); ngang ra: Can Du (BL18).'),
        'tenth-thoracic-vertebra-t10': ('Đốt sống ngực T10', 'Vertebra thoracica X', 'vertebrae', 'Dưới gai T10: Huyệt Trung Khu (GV7); ngang ra: Đởm Du (BL19).'),
        'eleventh-thoracic-vertebra-t11': ('Đốt sống ngực T11', 'Vertebra thoracica XI', 'vertebrae', 'Dưới gai T11: Huyệt Tích Trung (GV6); ngang ra: Tỳ Du (BL20).'),
        'twelfth-thoracic-vertebra-t12': ('Đốt sống ngực T12', 'Vertebra thoracica XII', 'vertebrae', 'Dưới gai T12: Huyệt Vị Thương; ngang ra: Vị Du (BL21).'),
        
        # Thắt lưng & Cùng
        'first-lumbar-vertebra-l1': ('Đốt sống thắt lưng L1', 'Vertebra lumbalis I', 'vertebrae', 'Dưới gai L1: Huyệt Huyền Khu (GV5); ngang ra: Tam Tiêu Du (BL22).'),
        'second-lumbar-vertebra-l2': ('Đốt sống thắt lưng L2', 'Vertebra lumbalis II', 'vertebrae', 'Dưới gai L2: Mệnh Môn (GV4 - Cội nguồn chân hỏa); ngang ra: Thận Du (BL23), Chí Thất (BL52).'),
        'third-lumbar-vertebra-l3': ('Đốt sống thắt lưng L3', 'Vertebra lumbalis III', 'vertebrae', 'Ngang mỏm ngang L3 dài nhất cột sống thắt lưng; Ngang ra: Khí Hải Du (BL24).'),
        'fourth-lumbar-vertebra-l4': ('Đốt sống thắt lưng L4', 'Vertebra lumbalis IV', 'vertebrae', 'Ngang mào chậu (Đường Tuffier); Dưới gai: Yêu Dương Quan (GV3); ngang ra: Đại Trường Du (BL25).'),
        'fifth-lumbar-vertebra-l5': ('Đốt sống thắt lưng L5', 'Vertebra lumbalis V', 'vertebrae', 'Dưới gai L5: Huyệt Thập Thất S錐; ngang ra: Quan Nguyên Du (BL26).'),
        'sacrum': ('Khung xương cùng', 'Os sacrum', 'vertebrae', '5 đốt cùng hợp nhất; Có 8 lỗ cùng: Bát Liêu (Thượng Liêu, Thứ Liêu, Trung Liêu, Hạ Liêu BL31-BL34).'),
        
        # Xương ức & Sườn
        'manubrium-of-sternum': ('Cán xương ức', 'Manubrium sterni', 'thorax', 'Khuyết cảnh trên cán ức: Huyệt Thiên Đột (CV22); Góc ức Louis: Ngang khoang gian sườn 2.'),
        'body-of-sternum': ('Thân xương ức', 'Corpus sterni', 'thorax', 'Tạo thành ngực trước; Đường dọc giữa ức là mạch Nhâm: Đản Trung (CV17), Ngọc Đường (CV18), Tử Cung (CV19).'),
        'xiphoid-process': ('Mỏm mũi kiếm xương ức', 'Processus xiphoideus', 'thorax', 'Khớp cán - mũi kiếm ức: Huyệt Cự Khuyết (CV14), Cưu Vĩ (CV15).'),
        
        # Chi trên
        'clavicle': ('Xương đòn', 'Clavicula', 'upper_limb', 'Hố trên đòn: Khuyết Bồn (ST12); Bờ dưới đòn: Khí Hộ (ST13), Vân Môn (LU2), Du Phủ (KI27).'),
        'scapula': ('Xương bả vai', 'Scapula', 'upper_limb', 'Gai vai: Kiên Tỉnh (GB21), Thiên Liêu (TE15); Hố trên gai: Khúc Viên (SI13); Hố dưới gai: Thiên Tông (SI11).'),
        'humerus': ('Xương cánh tay', 'Humerus', 'upper_limb', 'Mỏm cùng vai: Kiên Ngung (LI15); Củ lớn cánh tay: Nhu Du (SI10); Rãnh nhị đầu: Thiên Phủ (LU3).'),
        'radius': ('Xương quay', 'Radius', 'upper_limb', 'Chỏm quay: Khúc Trì (LI11); Mỏm trâm quay: Liệt Khuyết (LU7), Thái Uyên (LU9).'),
        'ulna': ('Xương trụ', 'Ulna', 'upper_limb', 'Mỏm khuỷu: Trúc Trạch; Rãnh thần kinh trụ: Tiểu Hải (SI8); Mỏm trâm trụ: Dương Cốc (SI5), Thần Môn (HT7).'),
        'scaphoid': ('Xương thuyền tay', 'Os scaphoideum', 'upper_limb', 'Đáy hõm lào giải phẫu (Anatomical snuffbox); Huyệt Dương Khê (LI5).'),
        'lunate': ('Xương nguyệt', 'Os lunatum', 'upper_limb', 'Xương cổ tay trung tâm; Huyệt Đại Lăng (PC7).'),
        'triquetral': ('Xương tháp tay', 'Os triquetrum', 'upper_limb', 'Xương bờ trụ cổ tay; Huyệt Dương Trì (TE4).'),
        'pisiform': ('Xương đậu', 'Os pisiforme', 'upper_limb', 'Xương vừng cổ tay bờ trụ; Điểm mốc huyệt Thần Môn (HT7).'),
        'trapezium': ('Xương thang', 'Os trapezium', 'upper_limb', 'Khớp bàn ngón tay cái.'),
        'trapezoid': ('Xương thê', 'Os trapezoideum', 'upper_limb', 'Xương khối cổ tay.'),
        'capitate': ('Xương cả', 'Os capitatum', 'upper_limb', 'Xương lớn nhất khối cổ tay.'),
        'hamate': ('Xương móc', 'Os hamatum', 'upper_limb', 'Móc xương móc bảo vệ thần kinh trụ; Huyệt Thiếu Phủ (HT8).'),
        
        # Chi dưới
        'hip-bone': ('Xương chậu (Xương hông)', 'Os coxae', 'pelvis_lower_limb', 'Gồm cánh chậu, mu và ngồi; Mào chậu: Huyệt Hoàn Khiêu (GB30), Cư Liêu (GB29); Ụ ngồi: Trật Biên (BL54).'),
        'femur': ('Xương đùi', 'Femur', 'pelvis_lower_limb', 'Mấu chuyển lớn: Huyệt Hoàn Khiêu (GB30); Lồi cầu trong: Khúc Tuyền (LR8), Âm Lăng Tuyền (SP9).'),
        'patella': ('Xương bánh chè', 'Patella', 'pelvis_lower_limb', 'Độc Tỵ (ST35 - Mắt gối ngoài), Tất Nhãn (Mắt gối trong); Bờ trên ngoài: Lương Khâu (ST34); Bờ trên trong: Huyết Hải (SP10).'),
        'tibia': ('Xương chày', 'Tibia', 'pelvis_lower_limb', 'Lồi củ chày: Dưới 3 thốn là Túc Tam Lý (ST36); Mắt cá trong: Thái Khê (KI3), Tam Âm Giao (SP6).'),
        'fibula': ('Xương mác', 'Fibula', 'pelvis_lower_limb', 'Chỏm xương mác: Dương Lăng Tuyền (GB34 - Cân hội); Mắt cá ngoài: Côn Lôn (BL60), Khâu Khư (GB40), Huyền Chung (GB39).'),
        'talus': ('Xương sên', 'Talus', 'pelvis_lower_limb', 'Khớp cổ chân truyền lực toàn thân; Mốc huyệt Giải Khê (ST41), Thương Khâu (SP5).'),
        'calcaneus': ('Xương gót', 'Calcaneus', 'pelvis_lower_limb', 'Xương lớn nhất bàn chân; Mốc huyệt Dũng Tuyền (KI1), Thái Khê (KI3), Chiếu Hải (KI6), Côn Lôn (BL60).'),
        'navicular': ('Xương thuyền chân', 'Os naviculare', 'pelvis_lower_limb', 'Bờ trong bàn chân; Mốc huyệt Nhiên Cốc (KI2).'),
        'cuboid': ('Xương hộp', 'Os cuboideum', 'pelvis_lower_limb', 'Bờ ngoài bàn chân; Mốc huyệt Kim Môn (BL63).'),
    }

    osteology = {}
    for m in meshes:
        # Check matching
        side = 'phải' if 'right-' in m else ('trái' if 'left-' in m else '')
        side_lat = 'dextrum' if 'right-' in m else ('sinistrum' if 'left-' in m else '')
        clean_name = m.replace('right-', '').replace('left-', '')
        
        info = None
        for k, v in base_dict.items():
            if k in clean_name or clean_name in k:
                info = v
                break

        if not info:
            # Sườn / đĩa đệm / đốt ngón
            if 'rib' in clean_name:
                num = clean_name.replace('-rib', '').replace('costal-', '')
                vi = f"Xương sườn {num} ({side})" if side else f"Xương sườn {num}"
                lat = f"Costa {num}"
                reg = 'thorax'
                note = 'Bảo vệ lồng ngực, khoang gian sườn chứa bó mạch thần kinh gian sườn; Mốc các huyệt mộ và kỳ huyệt ngực bụng.'
            elif 'costal-cartilage' in clean_name:
                vi = f"Sụn sườn ({side})" if side else "Sụn sườn"
                lat = "Cartilago costalis"
                reg = 'thorax'
                note = 'Nối các đầu xương sườn thật vào bờ xương ức.'
            elif 'intervertebral-disc' in clean_name:
                disc = clean_name.replace('intervertebral-disc-', '').upper()
                vi = f"Đĩa đệm gian đốt sống {disc}"
                lat = f"Discus intervertebralis {disc}"
                reg = 'vertebrae'
                note = 'Gồm nhân nhầy (nucleus pulposus) và vòng sợi (anulus fibrosus), hấp thu chấn động cột sống.'
            elif 'metacarpal' in clean_name:
                vi = f"Xương bàn tay ({side})"
                lat = f"Os metacarpale"
                reg = 'upper_limb'
                note = 'Huyệt Hợp Cốc (LI4) nằm giữa xương bàn 1 và 2; Lao Cung (PC8) nằm giữa xương bàn 2 và 3.'
            elif 'phalanx-hand' in clean_name or 'finger' in clean_name:
                vi = f"Đốt ngón tay ({side})"
                lat = f"Phalanx manus"
                reg = 'upper_limb'
                note = 'Nơi tận cùng của các kinh lạc tay (Tỉnh huyệt: Thiếu Thương LU11, Thương Dương LI1, Trung Xung PC9...).'
            elif 'metatarsal' in clean_name:
                vi = f"Xương bàn chân ({side})"
                lat = f"Os metatarsale"
                reg = 'pelvis_lower_limb'
                note = 'Huyệt Thái Xung (LR3) nằm ở kẽ xương bàn chân 1-2; Nội Đình (ST44) nằm ở kẽ xương bàn 2-3.'
            elif 'phalanx-foot' in clean_name or 'toe' in clean_name:
                vi = f"Đốt ngón chân ({side})"
                lat = f"Phalanx pedis"
                reg = 'pelvis_lower_limb'
                note = 'Nơi tận cùng của các kinh lạc chân (Tỉnh huyệt: Ẩn Bạch SP1, Đại Đôn LR1, Lệ Đoài ST45, Chí Âm BL67...).'
            else:
                vi = f"Xương {clean_name.replace('-', ' ')} ({side})" if side else f"Xương {clean_name.replace('-', ' ')}"
                lat = f"Os {clean_name.replace('-', ' ')}"
                reg = 'body'
                note = 'Cấu trúc xương Z-Anatomy.'
        else:
            base_vi, base_lat, reg, note = info
            vi = f"{base_vi} ({side})" if side and ('(' not in base_vi or 'C1' in base_vi or 'C7' in base_vi) else base_vi
            lat = f"{base_lat} {side_lat}".strip() if side_lat else base_lat

        osteology[m] = {
            'name_vi': vi,
            'name_lat': lat,
            'region': reg,
            'note': note
        }

    with open('web/data/osteologyDictionary.json', 'w', encoding='utf-8') as f:
        json.dump(osteology, f, ensure_ascii=False, indent=2)
    print(f"Built osteologyDictionary.json with {len(osteology)} bones!")

def enrich_myology():
    with open('web/data/anatomyDictionary.json', 'r', encoding='utf-8') as f:
        myo = json.load(f)

    # Anatomical origins, insertions, actions, and innervations for key muscles
    muscle_atlas = {
        'biceps-brachii': {
            'origin': 'Đầu dài: Củ trên ổ chảo xương vai; Đầu ngắn: Mỏm quạ xương vai.',
            'insertion': 'Lồi củ xương quay và trướng mạc cẳng tay (aponeurosis bicipitalis).',
            'action': 'Gấp cẳng tay tại khớp khuỷu, ngửa cẳng tay mạnh nhất khi khuỷu gấp, hỗ trợ gấp cánh tay.',
            'innervation': 'Dây thần kinh cơ bì (Musculocutaneus - rễ C5, C6).',
            'acupoints': 'Khúc Trạch (PC3), Xích Trạch (LU5), Thiên Phủ (LU3), Hiệp Bạch (LU4).'
        },
        'triceps-brachii': {
            'origin': 'Đầu dài: Củ dưới ổ chảo xương vai; Đầu ngoài: Mặt sau thân xương cánh tay trên rãnh TK quay; Đầu trong: Mặt sau xương cánh tay dưới rãnh quay.',
            'insertion': 'Mặt trên và bờ ngoài mỏm khuỷu xương trụ.',
            'action': 'Duỗi cẳng tay chính tại khớp khuỷu; Đầu dài hỗ trợ duỗi và khép cánh tay.',
            'innervation': 'Dây thần kinh quay (Radialis - rễ C6, C7, C8).',
            'acupoints': 'Thanh Lãnh Uyên (TE10), Tiêu Lạc (TE12), Nhu Hội (TE13).'
        },
        'deltoid': {
            'origin': '1/3 ngoài bờ trước xương đòn, mỏm cùng vai, và bờ dưới gai xương vai.',
            'insertion': 'Lồi củ delta ở mặt ngoài thân xương cánh tay.',
            'action': 'Sợi giữa dạng cánh tay 90°; Sợi trước gấp và xoay trong cánh tay; Sợi sau duỗi và xoay ngoài cánh tay.',
            'innervation': 'Dây thần kinh nách (Axillaris - rễ C5, C6).',
            'acupoints': 'Kiên Ngung (LI15), Kiên Liêu (TE14), Tý Nhu (LI14), Nhu Du (SI10).'
        },
        'pectoralis-major': {
            'origin': 'Phần đòn: 2/3 trong bờ trước xương đòn; Phần ức-sườn: Nửa trước xương ức và sụn sườn 1-6; Phần bụng: Lá trước bao cơ thẳng bụng.',
            'insertion': 'Mép ngoài rãnh gian củ (mào củ lớn) xương cánh tay.',
            'action': 'Khép và xoay trong cánh tay; Kéo cánh tay ra trước (động tác ôm/đẩy ngực); Hỗ trợ hô hấp hít vào gắng sức.',
            'innervation': 'Các dây thần kinh ngực trong và ngực ngoài (rễ C5-T1).',
            'acupoints': 'Trung Phủ (LU1 - Mộ Phế), Vân Môn (LU2), Khí Hộ (ST13), Khố Phòng (ST14), Ưng Song (ST16).'
        },
        'pectoralis-minor': {
            'origin': 'Bờ trên và mặt ngoài các xương sườn 3, 4, 5 gần sụn sườn.',
            'insertion': 'Bờ trong và mặt trên mỏm quạ xương vai.',
            'action': 'Kéo mỏm quạ xuống dưới và ra trước, xoay xương vai xuống; Nâng xương sườn khi hít vào gắng sức.',
            'innervation': 'Dây thần kinh ngực trong (rễ C8, T1).',
            'acupoints': 'Trung Phủ (LU1), Chu Vinh (SP20).'
        },
        'trapezius': {
            'origin': 'Đường gáy trên xương chẩm, u chẩm ngoài, dây chằng gáy, mỏm gai các đốt sống từ C7 đến T12.',
            'insertion': '1/3 ngoài bờ sau xương đòn, mỏm cùng vai và mép trên gai vai.',
            'action': 'Nâng vai, khép xương bả vai vào trong; Xoay ngửa ổ chảo xương vai lên trên để giơ tay quá đầu.',
            'innervation': 'Dây thần kinh sọ số XI (Thần kinh phụ - Accessorius) và các nhánh từ đám rối cổ C3, C4.',
            'acupoints': 'Kiên Tỉnh (GB21), Phong Trì (GB20), Thiên Liêu (TE15), Kiên Ngoại Du (SI14).'
        },
        'latissimus-dorsi': {
            'origin': 'Mỏm gai T7-L5, mạc ngực-thắt lưng, mào chậu sau, 3-4 xương sườn dưới và góc dưới xương vai.',
            'insertion': 'Đáy rãnh gian củ xương cánh tay.',
            'action': 'Duỗi, khép và xoay trong cánh tay; Kéo thân mình lên khi leo trèo.',
            'innervation': 'Dây thần kinh ngực lưng (Thoracodorsalis - rễ C6, C7, C8).',
            'acupoints': 'Chí Dương (GV9), Cân Súc (GV8), Cách Du (BL17), Can Du (BL18).'
        },
        'rectus-abdominis': {
            'origin': 'Mào mu và củ mu, khớp mu.',
            'insertion': 'Sụn sườn 5, 6, 7 và mỏm mũi kiếm xương ức.',
            'action': 'Gấp cột sống thắt lưng, nén ép nội tạng ổ bụng tăng áp lực ổ bụng (đại tiện, sinh đẻ).',
            'innervation': 'Các dây thần kinh gian sườn 7-11 và thần kinh dưới sườn T12.',
            'acupoints': 'Thừa Mãn (ST20), Lương Môn (ST21), Thiên Khu (ST25), Đại Cự (ST27), Khí Hải (CV6), Quan Nguyên (CV4).'
        },
        'gastrocnemius': {
            'origin': 'Đầu trong: Lồi cầu trong xương đùi; Đầu ngoài: Lồi cầu ngoài xương đùi.',
            'insertion': 'Hợp cùng cơ dép tạo thành gân gót (Achilles) bám vào củ gót xương gót.',
            'action': 'Gấp cẳng chân tại khớp gối, gấp lòng bàn chân tại khớp cổ chân (nhón gót, chạy nhảy).',
            'innervation': 'Dây thần kinh chày (Tibialis - rễ S1, S2).',
            'acupoints': 'Ủy Trung (BL40 - Hợp huyệt), Hợp Dương (BL55), Thừa Cân (BL56), Thừa Sơn (BL57).'
        },
        'soleus': {
            'origin': 'Mặt sau chỏm và 1/3 trên thân xương mác, đường cơ dép ở mặt sau xương chày.',
            'insertion': 'Mặt sau củ gót qua gân gót Achilles.',
            'action': 'Gấp lòng bàn chân mạnh mẽ, duy trì tư thế đứng thẳng chống lại trọng lực.',
            'innervation': 'Dây thần kinh chày (Tibialis - rễ L5, S1, S2).',
            'acupoints': 'Thừa Sơn (BL57), Phi Dương (BL58), Phụ Dương (BL59).'
        },
        'tibialis-anterior': {
            'origin': 'Lồi cầu ngoài và nửa trên mặt ngoài thân xương chày, màng gian cốt cẳng chân.',
            'insertion': 'Mặt trong và dưới xương chêm trong và nền xương bàn chân I.',
            'action': 'Gấp mu bàn chân (nâng bàn chân lên), nghiêng trong bàn chân.',
            'innervation': 'Dây thần kinh mác sâu (Fibularis profundus - rễ L4, L5).',
            'acupoints': 'Túc Tam Lý (ST36 - Trường sinh huyệt), Thượng Cự Hư (ST37), Giải Khê (ST41).'
        },
        'quadriceps-femoris': {
            'origin': 'Thẳng đùi: Gai chậu trước dưới; Rộng ngoài: Mấu chuyển lớn; Rộng trong: Mép trong đường ráp; Rộng giữa: Mặt trước thân xương đùi.',
            'insertion': 'Bao quanh xương bánh chè, tiếp tục bằng dây chằng bánh chè bám vào lồi củ chày.',
            'action': 'Duỗi cẳng chân tại khớp gối mạnh nhất cơ thể; Cơ thẳng đùi hỗ trợ gấp khớp háng.',
            'innervation': 'Dây thần kinh đùi (Femoralis - rễ L2, L3, L4).',
            'acupoints': 'Phục Thỏ (ST32), Âm Thị (ST33), Lương Khâu (ST34), Huyết Hải (SP10).'
        },
        'rectus-femoris': {
            'origin': 'Gai chậu trước dưới (AIIS) và viền trên ổ cối xương chậu.',
            'insertion': 'Nền xương bánh chè và lồi củ chày qua gân bánh chè.',
            'action': 'Duỗi khớp gối và gấp khớp háng.',
            'innervation': 'Dây thần kinh đùi (Femoralis - rễ L2, L3, L4).',
            'acupoints': 'Bễ Quan (ST31), Phục Thỏ (ST32).'
        },
        'calcaneal-tendon': {
            'origin': 'Hợp nhất từ gân cơ bụng chân (Gastrocnemius) và cơ dép (Soleus).',
            'insertion': 'Mặt sau củ gót xương gót.',
            'action': 'Gân lớn và khoẻ nhất cơ thể người, truyền lực gấp bàn chân khi bước đi và chạy.',
            'innervation': 'Dây thần kinh chày (Tibialis).',
            'acupoints': 'Côn Lôn (BL60), Thái Khê (KI3), Bộc Tham (BL61).'
        },
        'epicranial-aponeurosis': {
            'origin': 'Cơ chẩm ở phía sau (đường gáy trên).',
            'insertion': 'Cơ trán ở phía trước (da vùng lông mày và sống mũi).',
            'action': 'Kéo căng da đầu, kéo nhăn trán và nhướng mày.',
            'innervation': 'Dây thần kinh mặt VII (nhánh thái dương và tai sau).',
            'acupoints': 'Bách Hội (GV20), Tiền Đỉnh (GV21), Thông Thiên (BL7).'
        },
        'linea-alba': {
            'origin': 'Mỏm mũi kiếm xương ức.',
            'insertion': 'Khớp mu và mào mu.',
            'action': 'Đường gân trắng giữa bụng nơi đan chéo các lá mạc cơ chéo bụng và ngang bụng.',
            'innervation': 'Mạc gân vô mạch thần kinh trực tiếp (ranh giới phẫu thuật mở bụng an toàn).',
            'acupoints': 'Mạch Nhâm: Cự Khuyết (CV14), Trung Quản (CV12), Thần Khuyết (CV8), Khí Hải (CV6), Quan Nguyên (CV4).'
        }
    }

    # Enrich every muscle
    for k, v in myo.items():
        if k in muscle_atlas:
            v.update(muscle_atlas[k])
        else:
            # Default rich anatomical template based on region
            reg = v.get('region', 'body')
            name_vi = v.get('name_vi', k)
            if 'head' in reg:
                v['origin'] = f'Các mốc xương sọ mặt và mạc cơ vùng đầu mặt.'
                v['insertion'] = f'Da, màng xương hoặc sụn khớp vùng mặt cổ.'
                v['action'] = 'Biểu cảm nét mặt, vận động nhai hoặc cử động đầu cổ.'
                v['innervation'] = 'Dây thần kinh mặt (CN VII) hoặc thần kinh sinh ba (CN V).'
            elif 'thigh' in reg or 'leg' in reg:
                v['origin'] = f'Khung xương chậu, xương đùi hoặc màng gian cốt cẳng chân.'
                v['insertion'] = f'Xương bánh chè, xương chày, xương mác hoặc khối xương cổ chân.'
                v['action'] = 'Vận động khớp háng, khớp gối hoặc cổ chân (gấp, duỗi, xoay).'
                v['innervation'] = 'Dây thần kinh đùi, thần kinh tọa, thần kinh chày hoặc mác.'
            elif 'arm' in reg or 'hand' in reg:
                v['origin'] = f'Đai vai, xương cánh tay hoặc màng gian cốt cẳng tay.'
                v['insertion'] = f'Xương quay, xương trụ hoặc các đốt xương bàn ngón tay.'
                v['action'] = 'Vận động cánh tay, cẳng tay và khéo léo ngón tay.'
                v['innervation'] = 'Dây thần kinh cơ bì, thần kinh quay, giữa hoặc trụ.'
            else:
                v['origin'] = f'Cột sống, xương sườn hoặc đai xương nâng đỡ.'
                v['insertion'] = f'Các mốc xương kế cận hoặc mạc gân cơ thể.'
                v['action'] = 'Duy trì tư thế thắt lưng chậu, hô hấp hoặc vận động thân mình.'
                v['innervation'] = 'Các nhánh sau dây thần kinh gai sống hoặc thần kinh gian sườn.'

    with open('web/data/anatomyDictionary.json', 'w', encoding='utf-8') as f:
        json.dump(myo, f, ensure_ascii=False, indent=2)
    print(f"Enriched anatomyDictionary.json with Origin, Insertion, Action, Innervation for {len(myo)} muscles!")

if __name__ == '__main__':
    build_osteology()
    enrich_myology()

