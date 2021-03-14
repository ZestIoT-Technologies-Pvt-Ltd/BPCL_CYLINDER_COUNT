cd /home/zestiot-bpcl-hyd/Cylinder_v1.9

Process1=$(pgrep -f -x "python3 test_app.py")
if [ ! -z "$Process1" -a "$Process1" != " " ]; then
        echo "test_app.py Running"
else
        echo "test_app.py is not running"
        python3 test_app.py &
fi
