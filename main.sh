cd /home/zestiot-bpcl-hyd/Cylinder_v1.14

Process1=$(pgrep -f -x "python3 main_storage.py")
if [ ! -z "$Process1" -a "$Process1" != " " ]; then
        echo "main_storage.py Running"
else
        echo "main_storage.py is not running"
        python3 main_storage.py &
fi
