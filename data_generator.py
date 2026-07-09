# type: ignore
import csv
import random
from faker import Faker

def generate_metadata_dataset(filename="document_metadata.csv", record_count=100000):
    fake = Faker()
    
    departments = ['Finance', 'Legal', 'Engineering', 'HR', 'Executive', 'Marketing']
    sensitivity_levels = ['Public', 'Internal', 'Confidential', 'Strictly_Confidential']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Document_ID', 'Author', 'Department', 'Sensitivity_Level', 'File_Size_MB', 'Upload_Date'])
        
        for _ in range(record_count):
            doc_id = fake.uuid4()
            author = fake.name()
            department = random.choice(departments)
            
            if department in ['Legal', 'Executive', 'Finance']:
                sensitivity = random.choices(sensitivity_levels, weights=[0.1, 0.3, 0.4, 0.2])[0]
            else:
                sensitivity = random.choices(sensitivity_levels, weights=[0.4, 0.4, 0.15, 0.05])[0]
                
            file_size = round(random.uniform(0.1, 1024.0), 2)
            upload_date = fake.date_between(start_date='-3y', end_date='today').isoformat()
            
            writer.writerow([doc_id, author, department, sensitivity, file_size, upload_date])

if __name__ == "__main__":
    print("Generating dataset...")
    generate_metadata_dataset()
    print("Dataset generation complete.")