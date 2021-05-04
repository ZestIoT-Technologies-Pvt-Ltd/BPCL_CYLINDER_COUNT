cd /home/zestiot-bpcl-hyd/Cylinder_v1.15

Process1=$(pgrep -f -x "python3 storing_video_normal.py")
if [ ! -z "$Process1" -a "$Process1" != " " ]; then
        echo "storing_video_normal.py Running"
else
        echo "storing_video_normal.py is not running"
        python3 storing_video_normal.py &
fi

