#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "No arguments provided"
    echo "./statTests.sh start|stop <expNo> <testNo>"

else

    EXPNO=$2
    TESTNO=$3

    if [ $1 = start ] && ( [ ! -z $2 ] && [ ! -z $3 ] ) ; then
        
        for i in `seq 1 6`; do
            ssh spyuser@esuser0$i  "dstat -tcymdn -C total -N eth1 --net-packets --disk-tps --disk-util -rpgs --vm --unix --fs --integer 10 > dstat$EXPNO-esuser0$i-$TESTNO.out &"
            ssh spyuser@esuser0$i "iostat -c -d -x -t -m  10  > iostat$EXPNO-esuser0$i-$TESTNO.out &"
        done

    elif [ $1 = stop ] && ( [ ! -z $2 ] && [ ! -z $3 ] ); then
        TESTFILE=~/stats/tests$2-resources-$3
        mkdir $TESTFILE
        for i in `seq 1 6`; do
                ssh spyuser@esuser0$i "pkill dstat ; pkill iostat ; scp *esuser0$i*.out esuser01:$TESTFILE/ ; rm *esuser0$i*.out"
        done 
    else
        echo "Arguments should be: start|stop <expNo> <testNo>"
    fi
    
fi
