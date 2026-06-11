# Bookstore Service Robot

Bu projede Gazebo ortamında çalışan bir TurtleBot3 robotu, kitapçı ortamında belirlenen görev noktalarına sırayla gitmektedir. Robot her noktaya ulaştıktan sonra kamera üzerinden QR kodu okuyarak doğru konumda olup olmadığını kontrol eder. Görevlerin sonunda başarılı, atlanan veya başarısız olan noktalar için bir rapor oluşturulur.

## Kullanılan Sistem

* ROS Noetic
* Gazebo
* TurtleBot3 Waffle Pi
* AWS RoboMaker Bookstore World
* Python
* OpenCV
* AMCL
* move_base
* map_server

## Projede Yapılanlar

Projede öncelikle kitapçı ortamı Gazebo üzerinde çalıştırıldı. Daha sonra robotun bu ortamda kullanabileceği harita oluşturuldu ve `maps` klasörüne kaydedildi. Robotun harita üzerinde konumunu bulması için AMCL, hedeflere gitmesi için ise move_base kullanıldı.

Görev noktaları ve QR kod bilgileri `config/mission.yaml` dosyasında tutulmaktadır. Task manager node’u bu dosyayı okuyarak robotu sırayla hedeflere gönderir. Robot hedefe ulaştıktan sonra QR doğrulaması yapılır. QR kod doğru okunursa görev başarılı kabul edilir ve bir sonraki hedefe geçilir.

## Dış Bağımlılık

Bu depoda ana proje paketi bulunmaktadır:

```text
bookstore_service_robot
```

Simülasyon için AWS RoboMaker Bookstore World paketi de gereklidir. Bu paket aynı catkin workspace içindeki `src` klasöründe bulunmalıdır.

Beklenen klasör yapısı şu şekildedir:

```text
bookstore_final_ws/
└── src/
    ├── bookstore_service_robot/
    └── aws-robomaker-bookstore-world/
```

AWS paketi workspace içinde yoksa proje çalıştırılmadan önce `src` klasörüne eklenmelidir.

## Klasör Yapısı

```text
bookstore_service_robot/
├── config/
│   └── mission.yaml
├── launch/
│   ├── simulation.launch
│   ├── slam.launch
│   ├── navigation.launch
│   └── task_manager.launch
├── maps/
│   ├── map.yaml
│   └── map.pgm
├── models/
│   ├── qr_checkout_area/
│   ├── qr_information_desk/
│   ├── qr_novel_section/
│   ├── qr_science_section/
│   └── qr_images/
├── reports/
│   └── mission_report.txt
├── src/
│   ├── task_manager.py
│   └── qr_reader.py
├── world/
│   └── bookstore_qr.world
├── CMakeLists.txt
├── package.xml
└── README.md
```

## Görev Noktaları

Robotun gitmesi gereken noktalar `mission.yaml` dosyasında tanımlıdır.

Projede kullanılan görev noktaları:

* NOVEL_SECTION
* CHECKOUT_AREA
* SCIENCE_SECTION
* INFORMATION_DESK

Her nokta için hedef koordinatı ve beklenen QR metni bulunmaktadır. Örneğin bir görev noktasına gidildiğinde robotun okuması gereken QR metni şu formatta olur:

```text
LOCATION=NOVEL_SECTION
```

## Projeyi Derleme

Workspace klasörüne girilip proje derlenir:

```bash
cd ~/bookstore_final_ws
catkin_make
source devel/setup.bash
```

## Simülasyonu Başlatma

İlk terminalde Gazebo ortamı başlatılır:

```bash
source ~/bookstore_final_ws/devel/setup.bash
roslaunch bookstore_service_robot simulation.launch
```

Bu komut kitapçı ortamını, robotu ve QR kod modellerini Gazebo içinde başlatır.

## Navigasyonu Başlatma

İkinci terminalde navigation başlatılır:

```bash
source ~/bookstore_final_ws/devel/setup.bash
roslaunch bookstore_service_robot navigation.launch
```

RViz açıldıktan sonra robotun başlangıç konumu harita üzerinde **2D Pose Estimate** ile ayarlanır.

## Kamera Görüntüsünü Açma

QR kodun kamerada görünüp görünmediğini kontrol etmek için isteğe bağlı olarak şu komut kullanılabilir:

```bash
source ~/bookstore_final_ws/devel/setup.bash
rqt_image_view /camera/rgb/image_raw
```

## Görev Sistemini Başlatma

Üçüncü terminalde task manager ve QR reader başlatılır:

```bash
source ~/bookstore_final_ws/devel/setup.bash
roslaunch bookstore_service_robot task_manager.launch
```

Bu aşamadan sonra robot görev noktalarına sırayla gitmeye başlar. Her noktaya ulaştığında QR doğrulaması yapılır. Doğrulama başarılı olursa bir sonraki göreve geçilir.

## Görev Raporu

Görev sonunda oluşan rapor şu dosyaya yazılır:

```text
reports/mission_report.txt
```

Raporu terminalden görmek için:

```bash
cat ~/bookstore_final_ws/src/bookstore_service_robot/reports/mission_report.txt
```

## Harita Oluşturma

Harita oluşturmak için önce simülasyon başlatılır:

```bash
source ~/bookstore_final_ws/devel/setup.bash
roslaunch bookstore_service_robot simulation.launch
```

Daha sonra yeni bir terminalde SLAM başlatılır:

```bash
source ~/bookstore_final_ws/devel/setup.bash
roslaunch bookstore_service_robot slam.launch
```

Robot ortamda gezdirildikten sonra harita şu komutla kaydedilir:

```bash
rosrun map_server map_saver -f ~/bookstore_final_ws/src/bookstore_service_robot/maps/map
```

Bu işlem sonucunda `map.yaml` ve `map.pgm` dosyaları oluşur.

## Kullanılan ROS Topicleri

Projede kullanılan başlıca topicler:

* `/camera/rgb/image_raw`
* `/qr_text`
* `/cmd_vel`
* `/map`
* `/amcl_pose`
* `/move_base/goal`
* `/move_base/status`

## Kullanılan Node’lar

### task_manager.py

Bu node görevlerin yönetildiği ana node’dur. `mission.yaml` dosyasındaki hedefleri okur, move_base üzerinden robota hedef gönderir, hedefe ulaşıldıktan sonra QR doğrulamasını bekler ve sonuçları rapor dosyasına kaydeder.

### qr_reader.py

Bu node kameradan görüntü alır ve OpenCV kullanarak QR kod okumaya çalışır. Okunan QR metni `/qr_text` topic’i üzerinden yayınlanır.

## Hata Kontrolü

Projede bazı hata durumları için kontrol eklenmiştir:

* Robot hedefe ulaşamazsa timeout oluşur.
* Hedefe ulaşılamazsa tekrar deneme yapılır.
* QR kod okunamazsa belirli süre beklenir.
* QR doğrulanamazsa görev başarısız veya atlandı olarak rapora yazılır.

## Genel Çalışma Sırası

```text
Gazebo başlatılır.
Navigation başlatılır.
RViz üzerinden robotun başlangıç konumu ayarlanır.
Task manager başlatılır.
Robot ilk hedefe gider.
Hedefe ulaşınca QR doğrulaması yapılır.
QR doğruysa sıradaki hedefe geçilir.
Tüm görevler bitince rapor oluşturulur.
```

## Demo Videosunda Gösterilenler

Demo videosunda genel olarak şu adımlar gösterilecektir:

1. Gazebo ortamının açılması
2. RViz üzerinde harita ve robot konumu
3. Robotun görev noktalarına gitmesi
4. QR kod doğrulaması
5. Görev raporunun görüntülenmesi
