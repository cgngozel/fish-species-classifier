import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "1"
import warnings
warnings.filterwarnings("ignore")
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, RandomFlip, RandomRotation, RandomZoom
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping, Callback
from tensorflow.keras.applications import MobileNetV2

# manuel stopping: to stop and save create stop.txt in the file
class ManuelDurdurmaCallback(Callback):
    def __init__(self, dosya_adi="stop.txt"):
        super(ManuelDurdurmaCallback, self).__init__()
        self.dosya_adi = dosya_adi
        if os.path.exists(self.dosya_adi):
            os.remove(self.dosya_adi)
            
    def on_epoch_end(self, epoch, logs=None):
        if os.path.exists(self.dosya_adi):
            print(f"\n '{self.dosya_adi}' dosyası algılandı! Eğitim {epoch+1}. epochta kullanıcı tarafından durduruluyor...")
            self.model.stop_training = True
            os.remove(self.dosya_adi)

data = tf.keras.utils.image_dataset_from_directory(
    'data', 
    image_size=(256, 256), 
    batch_size=32,
    shuffle=True, 
    seed=42
)

data = data.map(lambda x, y: (x / 255.0, y))

total_batches = len(data)
train_size = int(total_batches * 0.7)
validation_size = int(total_batches * 0.2) 

train = data.take(train_size)
val = data.skip(train_size).take(validation_size)
test = data.skip(train_size + validation_size) 

AUTOTUNE = tf.data.AUTOTUNE
train = train.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val = val.cache().prefetch(buffer_size=AUTOTUNE)
test = test.cache().prefetch(buffer_size=AUTOTUNE)

#after trying with self conv2d layers results were inconsistent, switched to mobilenetv2.
base_model = MobileNetV2(input_shape=(256, 256, 3), include_top=False, weights='imagenet') 
base_model.trainable = False

data_augmentation = Sequential([
    RandomFlip("horizontal_and_vertical"),
    RandomRotation(0.15),
    RandomZoom(0.15),
])

model = Sequential([
    tf.keras.layers.Input(shape=(256, 256, 3)),
    data_augmentation,
    base_model,
    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(9, activation='softmax')
])

model.compile(optimizer="adam", loss=tf.keras.losses.SparseCategoricalCrossentropy(), metrics=["accuracy"])

logdir = "logs"
tensorboard_callback = TensorBoard(log_dir=logdir)
early_stopping_callback = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1)

manuel_durdur = ManuelDurdurmaCallback()

history = model.fit(
    train, 
    epochs=20, 
    validation_data=val, 
    callbacks=[tensorboard_callback, early_stopping_callback, manuel_durdur]
)

test_loss, test_accuracy = model.evaluate(test)
print(f"\nTest Kaybı (Loss): {test_loss:.4f}")
print(f"Test Doğruluğu (Accuracy): {test_accuracy:.4f}")


model.save("fish_species_model.keras")
print("\nModel 'fish_species_model.keras' saved.")