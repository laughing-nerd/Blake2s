import math

#Blake2 constants
SIGMA = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
    [11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4],
    [7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8],
    [9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13],
    [2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9],
    [12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11],
    [13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10],
    [6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5],
    [10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0]
] #This is a 10x16 matrix

R = [16, 12, 8, 7] #G Rotations
IV = [0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1, 0x510e527fade682d1, 0x9b05688c2b3e6c1f, 0x1f83d9abfb41bd6b,
      0x5be0cd19137e2179] #Initialization vector
h=[] #State Vector

#Blake2s constants
r = 10 #r=10 for Blake 2s, r=12 for Blake2b
w = 64 #Number of bits in a word
bb=64 #Block bytes
nn=32

def G(v, a, b, c, d, x, y): #Blake2 Mixing function
    x=int(x,16)
    y=int(y,16)

    v[a] = (v[a] + v[b] + x) % 2**w
    v[d] = ((v[d] ^ v[a]) >> R[0]) ^ ((v[d] ^ v[a])<<(w-R[0]))
    v[c] = (v[c] + v[d]) % 2**w
    v[b] = ((v[b] ^ v[c]) >> R[1]) ^ ((v[b] ^ v[c])<<(w-R[1]))
    v[a] = (v[a] + v[b] + y) % 2**w
    v[d] = ((v[d] ^ v[a]) >> R[2]) ^ ((v[d] ^ v[a])<<(w-R[2]))
    v[c] = (v[c] + v[d]) % 2**w
    v[b] = ((v[b] ^ v[c]) >> R[3]) ^ ((v[b] ^ v[c])<<(w-R[3]))

    return v


def F(h, m, t, f): #Blake2 Compression function
    v=h+IV
    v[12] = v[2] ^ (t % w**w)
    v[13] = v[13] ^ (t >> w)
    if (f==True):
        v[14] = ~v[14] 
    s=list()
    for i in range(r):
        s = SIGMA[i%10]
        v = G(v, 0, 4,  8, 12, m[s[0]], m[s[1]])
        v = G(v, 1, 5,  9, 13, m[s[2]], m[s[3]])
        v = G(v, 2, 6, 10, 14, m[s[4]], m[s[5]])
        v = G(v, 3, 7, 11, 15, m[s[6]], m[s[7]])
        v = G(v, 0, 5, 10, 15, m[s[8]], m[s[9]])
        v = G(v, 1, 6, 11, 12, m[s[10]], m[s[11]])
        v = G(v, 2, 7,  8, 13, m[s[12]], m[s[13]])
        v = G(v, 3, 4,  9, 14, m[s[14]], m[s[15]])
    for i in range(8):
        h[i] = h[i] ^ v[i] ^ v[i+8]
    
    return h

def pad(s, n, character='0'): #Helper function
    s=s+character*n
    return s


if __name__ == '__main__':
    message = input("Enter the message: ")
    ll = len(message)
    key = input("Enter the key : ")
    kk = len(key)

    dd=math.ceil(kk/bb) + math.ceil(ll/bb)
    if dd==0: #If no message and no key is provided then initialize dd as 1
        dd=1

    d=dict()
    for i in range(dd):
        d.update({i: []})

    #------------------------------------------------ Message Pre-processing ------------------------------------------------#
    newMessage = key + message
    max_bits = bb//8
    l=len(newMessage) * 2
    message_to_be_processed=None
    if(l % max_bits!=0):
        nearest_quotient = math.ceil(l/max_bits)
        message_to_be_processed = pad(newMessage, (max_bits*nearest_quotient)-l, '\0')

    #Convert message to hexadecimal ASCII and store it in Little Endian format
    message_to_be_processed = newMessage if message_to_be_processed==None else message_to_be_processed
    m = [hex(ord(c)).replace('0x', '') for c in message_to_be_processed]
    m=m[::-1]
    m=''.join(m)

    break_point=bb*2
    total_length_of_d = dd * bb * 2
    m = m+"0"*(total_length_of_d - len(m))
    count=0
    tempString=""
    for i in range(len(m)):
        tempString+=m[i]
        count+=1
        if (count==max_bits):
            d[i//break_point].append(tempString)
            count=0
            tempString=""
    #------------------------------------------------------------------------------------------------------------------------#

    #------------------------------------------------------- Blake2 -------------------------------------------------------#
    h = IV
    h[0] = h[0] ^ 0x01010000 ^ (kk<<8) ^ nn
    
    if (dd>1):
        for i in range(dd-1):
            h = F(h, d[dd-1], ll, True)
    else:
        h = F(h, d[dd-1], ll+bb, True)
    
    # print(h)
    result=[]
    for wrd in h[:nn//4]:
        bytes_ = wrd.to_bytes(300, byteorder="little")
        for b in bytes_:
            result.append(str(b))
    output = ''.join(result)
    print(hex(int(output)))
