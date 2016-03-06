#!/usr/bin/python
import random

def randPriv():
    ip1 = random.choice([172,192,10]) 
    if (int(ip1) == 172):
        ip2 = random.randint(16,31)            
        ip3 = random.randint(0,255)
        ip4 = random.randint(1,254)

    else:    
        ip2 = random.randint(0,255)
        ip3 = random.randint(0,255)        
        ip4 = random.randint(1,254)
    return ".".join(map(str,([ip1,ip2,ip3,ip4])))
    

def randPub():
    ip1 = random.randint(1,254)
    while (int(ip1) == 192 or int(ip1) == 10):
            ip1 = random.randint(1,254)
    ip2 = random.randint(0,255)
    while (int(ip1) == 172 and (int(ip2) >= 16 and int(ip2) <=31)):
            ip2 = random.randint(0,255)
    ip3 = random.randint(0,255)
    ip4 = random.randint(1,254)
    
    return ".".join(map(str,([ip1,ip2,ip3,ip4])))

infile = open('/home/spyuser/trafficPcap/smia.txt','r')
outfile = open('/home/spyuser/jsonIPmap2.txt', 'w')
first = True
#outfile.write('{\n')
ipList = list()
#try:
for line in infile:
    line2list = line.split(',')
    srcIP = line2list[9]
    dstIP = line2list[10]
    
    #srcIPpriv = randPriv()
    #dstIPpriv = randPriv()
    srcIPpub = randPub()
    dstIPpub = randPub()
    ipPub = randPub()
    #json.dump({ipPriv: ipPub}, outfile,indent=2)

    if first: 
        #outfile.write('%s: %s' %(srcIP, srcIPpriv))
        outfile.write('%s: %s' %(srcIP, srcIPpub))
        #outfile.write('\n%s: %s' %(dstIP, dstIPpriv))
        outfile.write('\n%s: %s' %(dstIP, dstIPpub))
        first = False
        ipList.append(srcIP)
        ipList.append(dstIP)
    else:
        outfile.write('\n%s: %s' %(ipPub, srcIPpub))
        if srcIP not in ipList:
            #outfile.write('\n%s: %s' %(srcIP, srcIPpriv))
            outfile.write('\n%s: %s' %(srcIP, srcIPpub))
            ipList.append(srcIP)

        if dstIP not in ipList:
            #outfile.write('\n%s: %s' %(dstIP, dstIPpriv))
            outfile.write('\n%s: %s' %(dstIP, dstIPpub))
            ipList.append(dstIP)
#except KeyboardInterrupt:
#outfile.write('\n}')

#print ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
infile.close()
outfile.close()
