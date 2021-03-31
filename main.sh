cd /home/zestiot-bpcl-hyd/Cylinder_v1.11/Cylinder_v1.10

Process1=$(pgrep -f -x "python3 main.py")
if [ ! -z "$Process1" -a "$Process1" != " " ]; then
        echo "main.py Running"
else
        echo "main.py is not running"
        python3 main.py &
fi
