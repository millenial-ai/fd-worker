aws configure set region $(aws configure list | grep region | awk '{print $2}')

cd ~/fd-worker

echo "Starting app"

source ~/.bashrc

nohup bash "run-${env:-production}.sh" > /dev/null 2>&1 &