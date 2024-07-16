# Запись видео и звука с внешнего устройства
ffmpeg -f v4l2 -video_size 1280x720 -i /dev/video0 -f alsa -i default -c:v libx264 -crf 23 -preset ultrafast -c:a aac -strict experimental output_video.mp4

# Запись экрана монитора
ffmpeg -f x11grab -video_size 1600x900 -framerate 50 -i :1.0+129,57 -vf format=yuv420p output.mp4

# Создание эффекта картинка в картинке
ffmpeg -i output.mp4 -i output_video.mp4 -filter_complex "[0:v][1:v]overlay=10:10[out]" -map "[out]" output_pip.mp4

# Наложение аудиодрожки на основное видео
ffmpeg -i output_video.mp4 -i output_pip.mp4 \
  -filter_complex "[0:v][1:v] overlay=W-w-10:H-h-10" \
  -map 0:v -map 1:v -map 0:a \
  -c:v libx264 -crf 23 -preset veryfast \
  -c:a aac -b:a 192k \
  output_with_audio.mp4



