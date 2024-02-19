#!/bin/bash
service docker start
dockerId=`sudo docker ps -aq`
clear
echo "1-Farm start 
2-Farm stop
3-Farm install
4-Farm delete
5-Farm reinstall
-----------------"

read  -p 'Yapmak istediğiniz işlemin rakamını girin: ' islem

if [[ $islem == 1 ]]; then
	clear
	echo "Farm başlatılıyor"
	#service docker start
	docker start $dockerId
	docker attach $dockerId
fi

if [[ $islem == 2 ]]; then
	clear
	echo "Farm durduruluyor"
	docker stop $dockerId
fi

if [[ $islem == 3 ]]; then
	clear
	echo "Farm kuruluyor"
	sudo docker run -v /media/yedekleme/github/:/git -v /media/yedekleme/farm/archives/:/var/cache/pisi/archives -v /media/yedekleme/farm/packages/:/var/cache/pisi/packages -v /media/yedekleme/farm/var/pisi/:/var/pisi -itd --security-opt=seccomp:unconfined pisilinux/chroot:latest bash
fi

if [[ $islem == 4 ]]; then
	clear
	echo "Farm siliniyor"
	sudo docker system prune -a
	sudo docker rm -f $dockerId
	sudo docker image rm pisilinux/chroot:latest
fi

if [[ $islem == 5 ]]; then
	clear
	echo "Farm sistemden kaldırılıyor"
	sudo docker system prune -a
	sudo docker rm -f $dockerId
	sudo docker image rm pisilinux/chroot
	clear
	echo "Sistem temizlendi
	Farm yeniden kuruluyor"
	sudo docker run -v /media/yedekleme/github/:/git -v /media/yedekleme/farm/archives/:/var/cache/pisi/archives -v /media/yedekleme/farm/packages/:/var/cache/pisi/packages -v /media/yedekleme/farm/var/pisi/:/var/pisi -itd --security-opt=seccomp:unconfined pisilinux/chroot:latest bash
fi

