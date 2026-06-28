import os
import shutil

def organize_and_clean_dataset(data_directory="data"):
    print("🧹 Veri seti düzenleme ve temizleme işlemi başlatıldı...\n")
    
    if not os.path.exists(data_directory):
        print(f"❌ Hata: '{data_directory}' klasörü bulunamadı.")
        return

    # clean mask/gt files from the dataset.
    for item in os.listdir(data_directory):
        item_path = os.path.join(data_directory, item)
        if os.path.isdir(item_path) and ("GT" in item or "- GT" in item):
            print(f"🗑️ SİLİNDİ (Maske Klasörü): {item}")
            shutil.rmtree(item_path)

    # move nested files.
    for item in os.listdir(data_directory):
        item_path = os.path.join(data_directory, item)
        
        if os.path.isdir(item_path):
            sub_items = os.listdir(item_path)
           
            if item in sub_items:
                nested_folder_path = os.path.join(item_path, item)
                temp_path = os.path.join(data_directory, f"{item}_temp_move")
                
                shutil.move(nested_folder_path, temp_path)
                shutil.rmtree(item_path)
                os.rename(temp_path, item_path)
                print(f"DÜZLEŞTİRİLDİ (Resimler yukarı taşındı): data/{item}/")

    print("you can execute train.py now")

if __name__ == "__main__":
    organize_and_clean_dataset("data")