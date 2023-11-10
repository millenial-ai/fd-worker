aws configure set region $(aws configure list | grep region | awk '{print $2}')

cd ~/fd-worker

echo "Starting app"

bash "run-${env:-production}.sh"