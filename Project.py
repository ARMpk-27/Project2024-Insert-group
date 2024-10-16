import struct
import time
import datetime


disaster_types = ["พายุ", "น้ำท่วม", "ภัยแล้ง", "ดินถล่ม"]


def select_disaster_type():
    print("ประเภทภัยพิบัติ:")
    for i, dtype in enumerate(disaster_types, start=1):
        print(f"{i}. {dtype}")
    while True:
        try:
            choice = int(input("เลือกประเภทภัย (1-4): "))
            if 1 <= choice <= len(disaster_types):
                return choice
            else:
                print("การเลือกไม่ถูกต้อง กรุณาเลือกใหม่")
        except ValueError:
            print("กรุณาใส่ตัวเลขที่ถูกต้อง")


record_format = 'ii30sifii20s'  
record_size = struct.calcsize(record_format)


def format_string(value, size):
    encoded = value.encode('utf-8')
    if len(encoded) > size:
   
        encoded = encoded[:size]
    return encoded.ljust(size, b'\x00')


def add_record(file_name, disaster_id, disaster_type_code, disaster_location, 
               num_volunteers, severity_measure, num_injured, num_deaths, timestamp):
    records = []
    
    try:
        with open(file_name, 'rb') as f:
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) == record_size:
                    try:
                        unpacked_data = struct.unpack(record_format, record)
                        records.append(unpacked_data)
                    except struct.error as e:
                        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                        continue 
    except FileNotFoundError:
        pass  

    for record in records:
        if record[0] == disaster_id:
            print("ID นี้มีอยู่แล้ว กรุณาเลือก ID ใหม่")
            return

    new_record = (
        disaster_id,
        disaster_type_code,      
        format_string(disaster_location, 30),  
        num_volunteers,
        severity_measure,
        num_injured,
        num_deaths,
        format_string(timestamp, 20) 
    )
    records.append(new_record)

    try:
        with open(file_name, 'wb') as f:
            for record in records:
                packed_data = struct.pack(
                    record_format,
                    record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5],
                    record[6],
                    record[7]
                )
                f.write(packed_data)
        print("เพิ่มข้อมูลสำเร็จ")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการบันทึกข้อมูล: {e}")

def display_records_by_disaster_type(file_name):
    disaster_type_choice = select_disaster_type()

    selected_disaster_type_code = disaster_type_choice  
    selected_disaster_type = disaster_types[disaster_type_choice - 1]

    try:
        with open(file_name, 'rb') as f:
            print(f"\nแสดงข้อมูลสำหรับภัยพิบัติ: {selected_disaster_type}")
            
            
            header = f"{'ID':<5} {'ประเภท':<10} {'สถานที่':<30} {'อาสาสมัคร':<12} {'ความรุนแรง':<15} {'บาดเจ็บ':<10} {'เสียชีวิต':<10} {'วันที่':<12}"
            print(header)
            print("-" * len(header))
            
            found = False  
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    print("ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง")
                    continue  

                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                    continue  

                disaster_type_code = unpacked_data[1]
                if disaster_type_code != selected_disaster_type_code:
                    continue  

                disaster_id = unpacked_data[0]
                disaster_location = unpacked_data[2].decode('utf-8', errors='replace').strip().replace('\x00', '')
                num_volunteers = unpacked_data[3]
                severity_measure = unpacked_data[4]
                num_injured = unpacked_data[5]
                num_deaths = unpacked_data[6]
                timestamp = unpacked_data[7].decode('utf-8', errors='replace').strip().replace('\x00', '')
                
                
                print(f"{disaster_id:<5} {disaster_types[disaster_type_code - 1]:<10} {disaster_location:<30} {num_volunteers:<12} {severity_measure:<15.2f} {num_injured:<10} {num_deaths:<10} {timestamp:<12}")
                found = True  

            if not found:
                print("ไม่พบข้อมูลสำหรับประเภทภัยพิบัติที่เลือก")
    except FileNotFoundError:
        print("ไม่พบไฟล์ข้อมูล")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")


def update_record(file_name, disaster_id):
    records = []
    updated = False
    
    try:
        with open(file_name, 'rb') as f:
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    print("ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง")
                    continue
                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                    continue 
                
                if unpacked_data[0] == disaster_id:
                    print("กรอกข้อมูลใหม่:")
                    disaster_type_code = select_disaster_type()
                    
                    disaster_location = input("สถานที่ภัยพิบัติ: ").strip()
                    if not disaster_location:
                        print("สถานที่ภัยพิบัติไม่สามารถว่างได้")
                        records.append(unpacked_data)
                        continue
                        
                    try:
                        num_volunteers = int(input("จำนวนอาสาสมัคร: "))
                        severity_measure = float(input("ค่าวัดความรุนแรง: "))
                        num_injured = int(input("จำนวนผู้บาดเจ็บ: "))
                        num_deaths = int(input("จำนวนผู้เสียชีวิต: "))
                    except ValueError:
                        print("กรุณาใส่ข้อมูลในรูปแบบที่ถูกต้องสำหรับจำนวนและค่าวัด")
                        records.append(unpacked_data)
                        continue
                        
                    timestamp = input("กรุณาใส่วันที่ (วัน/เดือน/ปี): ").strip()
                    
                   
                    if not timestamp:
                        timestamp = time.strftime("%d/%m/%Y")
                        
                   
                    new_record = (
                        disaster_id,
                        disaster_type_code,      
                        format_string(disaster_location, 30), 
                        num_volunteers,
                        severity_measure,
                        num_injured,
                        num_deaths,
                        format_string(timestamp, 20) 
                    )
                    records.append(new_record)  
                    updated = True
                else:
                    records.append(unpacked_data)

        if updated:
            try:
                with open(file_name, 'wb') as f:
                    for record in records:
                        packed_data = struct.pack(
                            record_format,
                            record[0],
                            record[1],
                            record[2],
                            record[3],
                            record[4],
                            record[5],
                            record[6],
                            record[7]
                        )
                        f.write(packed_data)
                print("อัปเดตข้อมูลสำเร็จ")
            except struct.error as e:
                print(f"ข้อผิดพลาดในการบันทึกข้อมูล: {e}")
        else:
            print("ไม่พบข้อมูลสำหรับการอัปเดต")
    except FileNotFoundError:
        print("ไม่พบไฟล์")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")


def delete_record(file_name, disaster_id):
    records = []
    deleted = False

    try:
        with open(file_name, 'rb') as f:
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    print("ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง")
                    continue
                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                    continue  

                if unpacked_data[0] != disaster_id:
                    records.append(unpacked_data)
                else:
                    deleted = True

        if deleted:
            # ขอการยืนยันจากผู้ใช้ก่อนลบ
            while True:
                confirm = input(f"คุณแน่ใจหรือไม่ว่าต้องการลบข้อมูล? (y/n): ")
                if confirm.lower() == 'y':
                    try:
                        with open(file_name, 'wb') as f:
                            for record in records:
                                packed_data = struct.pack(
                                    record_format,
                                    record[0],
                                    record[1],
                                    record[2],
                                    record[3],
                                    record[4],
                                    record[5],
                                    record[6],
                                    record[7]
                                )
                                f.write(packed_data)
                        print("ลบข้อมูลสำเร็จ")
                    except struct.error as e:
                        print(f"ข้อผิดพลาดในการบันทึกข้อมูล: {e}")
                    break
                elif confirm.lower() == 'n':
                    print("การลบข้อมูลถูกยกเลิก")
                    break
                else:
                    print("กรุณาใส่ 'y' หรือ 'n' เท่านั้น")
        else:
            print("ไม่พบข้อมูลสำหรับการลบ")
    except FileNotFoundError:
        print("ไม่พบไฟล์")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")


def display_all_records(file_name):
    try:
        with open(file_name, 'rb') as f:
            print("\nแสดงข้อมูลทั้งหมดของภัยพิบัติ")
            
            header = f"{'ID':<5} {'ประเภท':<10} {'สถานที่':<30} {'อาสาสมัคร':<12} {'ความรุนแรง':<15} {'บาดเจ็บ':<10} {'เสียชีวิต':<10} {'วันที่':<12}"
            print(header)
            print("-" * len(header))
            
            found = False
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    print("ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง")
                    continue

                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                    continue

                disaster_id = unpacked_data[0]
                disaster_type_code = unpacked_data[1]
                disaster_location = unpacked_data[2].decode('utf-8', errors='replace').strip().replace('\x00', '')
                num_volunteers = unpacked_data[3]
                severity_measure = unpacked_data[4]
                num_injured = unpacked_data[5]
                num_deaths = unpacked_data[6]
                timestamp = unpacked_data[7].decode('utf-8', errors='replace').strip().replace('\x00', '')

                print(f"{disaster_id:<5} {disaster_types[disaster_type_code - 1]:<10} {disaster_location:<30} {num_volunteers:<12} {severity_measure:<15.2f} {num_injured:<10} {num_deaths:<10} {timestamp:<12}")
                found = True

            if not found:
                print("ไม่มีข้อมูลในไฟล์")
    except FileNotFoundError:
        print("ไม่พบไฟล์ข้อมูล")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")

def generate_report(file_name, report_file):
    try:
        with open(file_name, 'rb') as f, open(report_file, 'w', encoding='utf-8') as report:
            # เขียนหัวข้อรายงาน
            report.write("รายงานข้อมูลภัยพิบัติ\n")
            report.write("=" * 130 + "\n\n")
        
            report.write("ข้อมูลภัยพิบัติทั้งหมด:\n")
            header = f"{'ID':<5} {'ประเภท':<12} {'สถานที่':<35} {'อาสาสมัคร':<15} {'ความรุนแรง':<15} {'บาดเจ็บ':<12} {'เสียชีวิต':<10} {'วันที่':<15}\n"
            report.write(header)
            report.write("-" * 130 + "\n")
            
            records = []
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    report.write(f"พบบันทึกที่ไม่ถูกต้อง (ขนาด: {len(record)} ไบต์)\n")
                    continue

                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    report.write(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}\n")
                    continue

                disaster_id = unpacked_data[0]
                disaster_type_code = unpacked_data[1]
                disaster_location = unpacked_data[2].decode('utf-8', errors='replace').strip().replace('\x00', '')
                num_volunteers = unpacked_data[3]
                severity_measure = unpacked_data[4]
                num_injured = unpacked_data[5]
                num_deaths = unpacked_data[6]
                timestamp = unpacked_data[7].decode('utf-8', errors='replace').strip().replace('\x00', '')

                # ตรวจสอบรหัสประเภทภัยพิบัติ
                if 1 <= disaster_type_code <= len(disaster_types):
                    disaster_type = disaster_types[disaster_type_code - 1]
                else:
                    disaster_type = f"ไม่ทราบ ({disaster_type_code})"

                line = f"{disaster_id:<5} {disaster_type:<12} {disaster_location:<35} {num_volunteers:<15} {severity_measure:<15.2f} {num_injured:<12} {num_deaths:<10} {timestamp:<15}\n"
                report.write(line)
                records.append(unpacked_data)

            if not records:
                report.write("ไม่มีข้อมูลในไฟล์\n")

            # เริ่มส่วนเปรียบเทียบข้อมูลภัยพิบัติ
            report.write("\nผลการเปรียบเทียบข้อมูลภัยพิบัติ:\n")
            report.write("=" * 130 + "\n")
            
            # จัดกลุ่มข้อมูลตามประเภทของภัยพิบัติ
            disaster_records = {dtype: {} for dtype in disaster_types}
            malformed_count = 0

            for unpacked_data in records:
                disaster_type_code = unpacked_data[1]
                if 1 <= disaster_type_code <= len(disaster_types):
                    disaster_type = disaster_types[disaster_type_code - 1]
                    disaster_location = unpacked_data[2].decode('utf-8', errors='replace').strip().replace('\x00', '')
                    timestamp_str = unpacked_data[7].decode('utf-8', errors='replace').strip().replace('\x00', '')
                    try:
                        timestamp = datetime.datetime.strptime(timestamp_str, "%d/%m/%Y")
                    except ValueError:
                        report.write(f"รูปแบบวันที่ไม่ถูกต้องสำหรับ ID {unpacked_data[0]}: {timestamp_str}\n")
                        malformed_count += 1
                        continue
                    
                    # จัดกลุ่มตามสถานที่ภายในประเภทภัยพิบัติ
                    if disaster_location not in disaster_records[disaster_type]:
                        disaster_records[disaster_type][disaster_location] = []
                    disaster_records[disaster_type][disaster_location].append((timestamp, unpacked_data))
                else:
                    report.write(f"รหัสประเภทภัยพิบัติไม่ถูกต้องสำหรับ ID {unpacked_data[0]}: {disaster_type_code}\n")
                    malformed_count += 1

            if malformed_count > 0:
                report.write(f"\nพบบันทึกที่ไม่ถูกต้องทั้งหมด: {malformed_count} รายการ\n")

            # ฟังก์ชันเปรียบเทียบค่า
            def compare(current, previous):
                difference = current - previous
                if difference > 0:
                    return "เพิ่มขึ้น", difference
                elif difference < 0:
                    return "ลดลง", abs(difference)
                else:
                    return "เท่าเดิม", 0

            # เปรียบเทียบข้อมูลสำหรับแต่ละประเภทภัยพิบัติและสถานที่
            for dtype, locations in disaster_records.items():
                report.write(f"\nการเปรียบเทียบข้อมูลสำหรับประเภทภัยพิบัติ: {dtype}\n")
                report.write("=" * 130 + "\n")
                if not locations:
                    report.write("ไม่มีข้อมูลสำหรับประเภทภัยพิบัตินี้\n")
                    continue
                for location, loc_records in locations.items():
                    report.write(f"\nสถานที่: {location}\n")
                    report.write("-" * 130 + "\n")
                    if len(loc_records) < 2:
                        report.write("มี 1 ข้อมูลไม่สามารถคำนวณได้\n")
                        continue
                    # เรียงลำดับบันทึกตามวันที่
                    loc_records.sort(key=lambda x: x[0])

                    latest_record = loc_records[-1][1]
                    previous_record = loc_records[-2][1]

                    latest_injured = latest_record[5]
                    latest_deaths = latest_record[6]
                    latest_severity = latest_record[4]

                    previous_injured = previous_record[5]
                    previous_deaths = previous_record[6]
                    previous_severity = previous_record[4]

                    injured_status, injured_diff = compare(latest_injured, previous_injured)
                    deaths_status, deaths_diff = compare(latest_deaths, previous_deaths)
                    severity_status, severity_diff = compare(latest_severity, previous_severity)

                    report.write(f"การเปรียบเทียบข้อมูลล่าสุดกับข้อมูลก่อนหน้า:\n")
                    if injured_diff != 0:
                        report.write(f"ผู้บาดเจ็บ: {previous_injured} → {latest_injured} ({injured_status} {injured_diff})\n")
                    else:
                        report.write(f"ผู้บาดเจ็บ: {previous_injured} → {latest_injured} ({injured_status})\n")
                    
                    if deaths_diff != 0:
                        report.write(f"ผู้เสียชีวิต: {previous_deaths} → {latest_deaths} ({deaths_status} {deaths_diff})\n")
                    else:
                        report.write(f"ผู้เสียชีวิต: {previous_deaths} → {latest_deaths} ({deaths_status})\n")
                    
                    if severity_diff != 0:
                        report.write(f"ความรุนแรง: {previous_severity:.2f} → {latest_severity:.2f} ({severity_status} {severity_diff:.2f})\n\n")
                    else:
                        report.write(f"ความรุนแรง: {previous_severity:.2f} → {latest_severity:.2f} ({severity_status})\n\n")

            # เพิ่มส่วนแยกสถานที่ตามความรุนแรง
            report.write("\nการจัดกลุ่มสถานที่ตามความรุนแรง:\n")
            report.write("=" * 130 + "\n")
            
            # กำหนดเกณฑ์ความรุนแรง
            
            def categorize_severity(severity):
                if severity >= 7.5:
                    return "สูง"
                elif severity >= 5.0:
                    return "กลาง"
                else:
                    return "ต่ำ"
            
            # สร้างโครงสร้างข้อมูลสำหรับจัดกลุ่มสถานที่ตามความรุนแรง
            severity_groups = {"สูง": set(), "กลาง": set(), "ต่ำ": set()}

            for unpacked_data in records:
                severity = unpacked_data[4]
                location = unpacked_data[2].decode('utf-8', errors='replace').strip().replace('\x00', '')
                category = categorize_severity(severity)
                severity_groups[category].add(location)

            # เขียนข้อมูลลงในรายงาน
            for category, locations in severity_groups.items():
                report.write(f"\nความรุนแรง: {category}\n")
                report.write("-" * 130 + "\n")
                if locations:
                    for loc in sorted(locations):
                        report.write(f"- {loc}\n")
                else:
                    report.write("ไม่มีสถานที่สำหรับความรุนแรงระดับนี้\n")
            report.write("-" * 130 + "\n")    


        print(f"สร้างรายงานสำเร็จแล้ว: {report_file}")
    except FileNotFoundError:
        print("ไม่พบไฟล์ข้อมูล")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")


def main():
    file_name = "disaster_data.bin"
    report_file = "disaster_report.txt" 

    while True:
        print("\nเมนู:")
        print("1. เพิ่มข้อมูล")
        print("2. แสดงข้อมูลตามประเภทของภัยพิบัติ")
        print("3. แสดงข้อมูลทั้งหมด")
        print("4. อัปเดตข้อมูล")
        print("5. ลบข้อมูล")
        print("6. สร้างรายงานข้อมูลและเปรียบเทียบ")
        print("7. ออกจากโปรแกรม")  # ปรับหมายเลขเมนู

        choice = input("เลือกเมนู (1-7): ")

        if choice == '1':
            try:
                disaster_id = int(input("กรุณาใส่ ID: "))
                disaster_type_code = select_disaster_type()
                
                disaster_location = input("กรุณาใส่สถานที่เกิดภัยพิบัติ: ").strip()
                if not disaster_location:
                    print("สถานที่เกิดภัยพิบัติไม่สามารถเป็นค่าว่างได้")
                    continue
                
                num_volunteers = int(input("อาสาสมัคร: "))
                severity_measure = float(input("ความรุนแรง: "))
                num_injured = int(input("จำนวนผู้บาดเจ็บ: "))
                num_deaths = int(input("จำนวนผู้เสียชีวิต: "))
                timestamp = input("กรุณาใส่วันที่ (วัน/เดือน/ปี): ").strip()
                if not timestamp:
                    timestamp = time.strftime("%d/%m/%Y")
                add_record(file_name, disaster_id, disaster_type_code, disaster_location, 
                           num_volunteers, severity_measure, num_injured, num_deaths, timestamp)
            except ValueError:
                print("กรุณาใส่ข้อมูลในรูปแบบที่ถูกต้อง")
        
        elif choice == '2':
            display_records_by_disaster_type(file_name)

        elif choice == '3':
            display_all_records(file_name)

        elif choice == '4':
            try:
                disaster_id = int(input("กรุณาใส่ ID ที่ต้องการอัปเดต: "))
                update_record(file_name, disaster_id)
            except ValueError:
                print("กรุณาใส่ ID ในรูปแบบตัวเลข")
        
        elif choice == '5':
            try:
                disaster_id = int(input("กรุณาใส่ ID ที่ต้องการลบ: "))
                delete_record(file_name, disaster_id)
            except ValueError:
                print("กรุณาใส่ ID ในรูปแบบตัวเลข")
        
        elif choice == '6':
            generate_report(file_name, report_file)  # เรียกใช้ฟังก์ชันใหม่

        elif choice == '7':
            print("ออกจากโปรแกรม")
            break

        else:
            print("กรุณาเลือกเมนูที่ถูกต้อง")

if __name__ == "__main__":
    main()
