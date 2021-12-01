import cv2 as cv
import numpy as np
from numpy import array, asarray
import time
import re

def show_Img(title,arr,x,y):
    img = np.zeros([x,y])
    i= 0
    for a in range(x):
        for b in range(y):
            img[a][b]=int(arr[i])
            i+=1

    cv.imwrite(title+"_output.png", img)
    #cv.imshow(title, img)
    #cv.waitKey() # waits until a key is pressed
    #cv.destroyAllWindows() # destroys the window showing image   

def bitmap(x):  #bit map for 0-255 pixel values
    #binary = bin(x)[2:] # remove 'b'  
    #print(binary)
    binary = '{0:08b}'.format(x)
    rsb = len(binary)-4
    lsbBin = binary[0:rsb]+"0000"
    return int(lsbBin,2)

def Lbitmap(x):  #bit map for -15 pixel values
    binary = '{0:08b}'.format(x) 
    #print(binary)
    rsb = len(binary)-4
    lsbBin = binary[rsb:len(binary)]+"0000"
    return int(lsbBin,2)

def bitmap_decode(x):   #return pixel value and how many occurances 1-15
    lsb = bitmap(x) #returns map value first 4 bits
    binary = bin(x)[2:]
    start = len(binary)-4
    rsb = binary[start:start+4] #return a value 1-15 for how many time the value occured
    rsb = int(rsb,2)
    
    #print(lsb,rsb)
    return lsb,rsb

def Lbitmap_decode(x):   #return lower pixel value and how many occurances 1-15
    binary = bin(x)[2:]
    a = len(binary)-4
    lsb = "0000"+binary[0:a]
    lsb = int(lsb,2)

    rsb = binary[a:a+4] #return a value 1-15 for how many time the value occured
    rsb = int(rsb,2)
    
    return lsb,rsb

def analysis(im1,im2,encode):
    x = (im1.shape[0]*im1.shape[1])
    X = ((x-len(encode))/x)*100
    print("Compression:",str(X))
    
    im2 = np.array(im2)
    im2 = im2.reshape(im1.shape[0],im1.shape[1])
    Y = np.square(np.subtract(im1,im2)).mean()
    print("MSE:", str(Y))

def analysis2(im1,im2,encode):
    x = (im1.shape[0]*im1.shape[1]*8)   #uncompressed 8 bit slices
    temp = 0
    for i in range(8):
        for j in encode[i]:
            temp +=1
    X = ((x-temp)/x)*100
    print("Compression:",str(X))
    
    Y = np.square(np.subtract(im1,im2)).mean()
    print("MSE:", str(Y))
#512*512 = 262,144
# *8 bits = 2,097,152
'''
#negative loseless rle compression
def test_RLE(data):
    data= data.flatten()
    temp = ""
    for i in range(len(data)):
        temp += f'{data[i]:8b}'
    i=
    n = len(temp)
    btemp =""
    while i < n-1:
        count = 1
        while(i<n-1 and temp[i]==temp[i+1]):
            count +=1
            i+=1
        if(temp[i] == "1"):
            btemp+="A"
        else:
            btemp+="B"
        btemp+=str(count)
        i+=1
    return btemp

def test_RLD(data,x,y):
    new_image = np.zeros([x,y])
    n = len(data)
    i=
    binary = ""
    while i<n-1:
        temp=""
        if(data[i]=="A"):
            temp="1"
        else:
            temp=""
        i+=1 
        for _ in range(int(data[i])):
            binary +=temp
        i+=1
    #print(binary)
    i=
    for a in range(x):
        for b in range(y):
            new_image[a][b]=int(binary[i:i+8],2)
            i+=8
    return new_image
'''

def RLE(data, Lower = None):
    data= data.flatten()
    b_map = []
    e_map = []
    #for i in range(512):
    for i in range(len(data)):
        if Lower == True:
            b_map.append(Lbitmap(data[i]))
        else:
            b_map.append(bitmap(data[i]))
    b_map = np.array(b_map)    

    i= 0
    n = b_map.shape[0]
    while i<n-1:
        count = 1
        j = i
        x = b_map[i]
        while j<n-1:
            if (b_map[i]==b_map[j+1]):
                count +=1
                j = j+1
            else:
                break
        i = j+1
        
        if count <=15:
            e_map.append(x+count)
        else:
            #print("warning"+str(count))
            while (count>0):
                if count>15:
                    e_map.append(x+15)
                    count -=15
                elif count<=15:
                    e_map.append(x+count)
                    break

    return e_map

def cRLE(data, tx,Lower = None):
    data= data.flatten()
    b_map = []
    e_map = []
    #print(len(data))
    for i in range(len(data)):
        if Lower == True:
            b_map.append(Lbitmap(data[i]))
        else:
            b_map.append(bitmap(data[i]))
    b_map = np.array(b_map) 
    #print(b_map.shape)     #shape of bitmap is correct

    i= 0
    n = b_map.shape[0]
    #print(n)
    totcnt = 0
    aptcnt =0
    highcnt =0
    while i<=n-1:
        count = 1
        x = b_map[i]
        j = i
        
        while j<n-1:
            if (b_map[j]==b_map[j+1]):
                count +=1
                j = j+1
            else:
                break
        
        totcnt += count
        if count < tx:   
            e_map.append(x+count)
            aptcnt+=1
        else:
            temp_cnt = count
            while(temp_cnt>tx):
                e_map.append(x+(tx-1))
                aptcnt+=1
                temp_cnt -= (tx-1)
            #print(temp_cnt)
            e_map.append(x+temp_cnt)
            aptcnt+=1

        
        
        #if count > highcnt: highcnt = count
        i = j+1
     
    #print(totcnt)
    #print("aptcnt:"+str(aptcnt))    
    #print("highcnt:"+str(highcnt))  
            

    return e_map   

def RLD(data,sz, Lower = None):
    n = len(data)
    arr = []
    i= 0
    
    while i < n-1:
        if Lower == True:
            a,b = Lbitmap_decode(data[i])
        else:
            a,b = bitmap_decode(data[i])
        for _ in range(b):
            arr.append(a)
        i+=1
    if len(arr) < sz:
        pad = sz-len(arr)
        for _ in range(pad):
            arr.append(0)
    
    return arr
  
def cRLD(data,sz, x, Lower = None):
    n = len(data)
    #print("aptlen",str(n))
    arr = []
    i= 0
    totcnt = 0
    aptcnt = 0
    while i < n-1:
        if data[i]>x:
            if Lower == True:
                a,b = Lbitmap_decode(data[i])
                
            else:
                a = x
                b = data[i]-x
        else:
            a = 0
            b = data[i]
        
        for _ in range(b):
            arr.append(a)
            totcnt += 1
        aptcnt += b
        i+=1
    if len(arr) < sz:
        pad = sz-len(arr)
        for _ in range(pad):
            arr.append(0)
    #print(totcnt)
    #print("aptcnt:"+str(aptcnt))  

    return arr

def RLE_BitSplice(data):
    a,b = data.shape
    lst = []
    for i in range(0, a):
        for j in range(0, b):
            lst.append(np.binary_repr(data[i][j] ,width=8))
    
    #before rle
    #Seperating bits into different bit arrays
    #t8 = (np.array([int(i[0]) for i in lst],dtype = np.uint8) * 128).reshape(a,b)
    #cv.imwrite("RLC_BP_t8_output.png", t8)
    
    eight_bit = cRLE((np.array([int(i[0]) for i in lst],dtype = np.uint8) * 128).reshape(a,b),128)
    seven_bit = cRLE((np.array([int(i[1]) for i in lst],dtype = np.uint8) * 64).reshape(a,b),64)
    six_bit = cRLE((np.array([int(i[2]) for i in lst],dtype = np.uint8) * 32).reshape(a,b),32)
    five_bit = cRLE((np.array([int(i[3]) for i in lst],dtype = np.uint8) * 16).reshape(a,b),16)
    four_bit = cRLE((np.array([int(i[4]) for i in lst],dtype = np.uint8) * 8).reshape(a,b),8,True)
    three_bit = cRLE((np.array([int(i[5]) for i in lst],dtype = np.uint8) * 4).reshape(a,b),4,True)
    two_bit = cRLE((np.array([int(i[6]) for i in lst],dtype = np.uint8) * 2).reshape(a,b),2,True)
    one_bit = RLE((np.array([int(i[7]) for i in lst],dtype = np.uint8) * 1).reshape(a,b),True)

    b_lst =[]
   
    b_lst.append(eight_bit)
    b_lst.append(seven_bit)
    b_lst.append(six_bit)
    b_lst.append(five_bit)
    b_lst.append(four_bit)
    b_lst.append(three_bit)
    b_lst.append(two_bit)
    b_lst.append(one_bit)
   
    return b_lst

def RLD_BP(b_list,a,b):
    sz=a*b
    eight = cRLD(b_list[0],sz,128)
    seven = cRLD(b_list[1],sz,64) 
    six = cRLD(b_list[2],sz,32) 
    five = cRLD(b_list[3],sz,16)
    four = cRLD(b_list[4],sz,8,True)
    three = cRLD(b_list[5],sz,4,True) 
    two = cRLD(b_list[6],sz,2,True) 
    one = cRLD(b_list[7],sz,1,True)
    
    new_image = np.zeros([a, b])
    i = 0
    for x in range(a):
        for y in range(b):
            new_image[x][y] = eight[i]+seven[i]+six[i]+five[i]+four[i]+three[i]+two[i]+one[i]
            i+=1
    return new_image

#Run length coding on the grayscale values
def RLC_GS(image):
    print("Running RLC_GS")
    data = asarray(image)
    a,b = image.shape
    start = time.time()
    encode = RLE(data)
    end = time.time()
    print(f"Encoding Runtime: {end - start}")
    start = time.time()
    decode = RLD(encode,a*b)
    end = time.time()
    print(f"Decoding Runtime: {end - start}")
    analysis(data,decode,encode)
    show_Img("RLC_GS",decode,a,b)
  
#Run length coding on the Bit planes
def RLC_BP(image):
    print("Running RLC_BP")
    data = asarray(image)
    a,b = image.shape
    
    start = time.time()
    encode = RLE_BitSplice(data)
    end = time.time()
    print(f"Encoding Runtime: {end - start}")
    
    start = time.time()
    decode = RLD_BP(encode,a,b)
    end = time.time()
    print(f"Decoding Runtime: {end - start}")

    analysis2(data,decode,encode)
    cv.imwrite("RLC_BP_output.png", decode)

#Variable length Huffman coding
def var_HC(image):
    data = asarray(image)
    t_data = data.flatten()
    a,b = image.shape

    data_list = str(t_data.tolist())
    start = time.time()
    pixel_values = []
    unique_values = []
    for val in data_list:
        if val not in pixel_values:
            frequency = data_list.count(val)             #frequency of each pixel value repetition
            pixel_values.append(frequency)
            pixel_values.append(val)
            unique_values.append(val)
    
    nodes = []
    while len(pixel_values) > 0:
        nodes.append(pixel_values[0:2])
        pixel_values = pixel_values[2:]                               # sorting according to frequency
    nodes.sort()
    h_tree = []
    h_tree.append(nodes)                             #Make each unique pixel value as a leaf node
   
    def c_nodes(nodes):                             #recursively called local node function
        pos = 0
        nnode = []
        if len(nodes) > 1:
            nodes.sort()
            nodes[pos].append("1")                       # assigning values 1 and 0
            nodes[pos+1].append("0")
            cnode1 = (nodes[pos] [0] + nodes[pos+1] [0])
            cnode2 = (nodes[pos] [1] + nodes[pos+1] [1])  # combining the nodes to generate pathways
            nnode.append(cnode1)
            nnode.append(cnode2)
            nnodes=[]
            nnodes.append(nnode)
            nnodes = nnodes + nodes[2:]
            nodes = nnodes
            h_tree.append(nodes)
            c_nodes(nodes)
        return h_tree                                     # huffman tree generation

    newnodes = c_nodes(nodes)

    h_tree.sort(reverse = True)

    c_list = []
    for level in h_tree:
        for node in level:
            if node not in c_list:
                c_list.append(node)
            else:
                level.remove(node)
    count = 0
    for level in h_tree:
        #print("Level", count,":",level)             #print huffman tree
        count+=1
    l_bin = []
    if len(unique_values) == 1:
        l_code = [unique_values[0], "0"]
        l_bin.append(l_code*len(data_list))
    else:
        for val in unique_values:
            code =""
            for node in c_list:
                if len (node)>2 and val in node[1]:           #genrating binary code
                    code = code + node[2]
            l_code =[val,code]
            l_bin.append(l_code)
    b_str =""
    for character in data_list:
        for item in l_bin:
            if character in item:
                b_str = b_str + item[1]
    binary ="0b"+b_str
    end = time.time()
    print(f"Encoding Runtime: {end - start}")
    
    start = time.time()   
    #output = open("compressed.txt","w+")
    #output.write(b_str)

    b_str = str(binary[2:])
    uc_str =""
    code =""
    for digit in b_str:
        code = code+digit
        pos=0                                        #iterating and decoding
        for val in l_bin:
            if code ==val[1]:
                uc_str=uc_str+l_bin[pos] [0]
                code=""
            pos+=1
    end = time.time()
    print(f"Decoding Runtime: {end - start}")

    temp = re.findall(r'\d+', uc_str)
    res = list(map(int, temp))
  
    res = np.array(res)
    res = res.astype(np.uint8)
    res = np.reshape(res, (a,b))
    
    x = len(data_list)*7
    X = ((x-len(binary)-2)/x)*100
    print("Compression:",str(X))
    
    Y = np.square(np.subtract(image,res)).mean()
    print("MSE:", str(Y))

    cv.imwrite("var_HC_output.png", res)

#LZW (for Extra credit only)
def LZW(image):
    data = asarray(image)
    a,b = image.shape
    new_image = np.zeros([a, b])

    return NotImplemented

def main():
    im = cv.imread("lena512.pgm")
    im = cv.cvtColor(im,cv.COLOR_BGR2GRAY)

    #print(bitmap(241))
    RLC_GS(im)
    RLC_BP(im)
    var_HC(im)
    #LZW(im)

if __name__ == "__main__":
    main()