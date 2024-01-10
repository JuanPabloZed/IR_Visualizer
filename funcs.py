from numpy import log2,ones,convolve,pad,hamming,asarray,max as maax

def padNhamm(data):
    npoutfile = asarray(data)/maax(data)
    pad_length = npow2(npow2(len(npoutfile)))
    padded_npoutfile = pad(npoutfile,(0,pad_length-len(npoutfile)),'constant',constant_values=(0,0))
    h_panned_npoutfile = padded_npoutfile*hamming(pad_length)
    return h_panned_npoutfile

def normalize(data):
    if data.ndim == 1:
        normdata = data/max(abs(data))
    elif data.ndim == 2:
        maxL = max(abs(data[:,0]))
        maxR = max(abs(data[:,1]))
        normdata = data/max([maxL,maxR])
    return normdata

def npow2(n):
    return 1 << (int(log2(n - 1)) + 1)

def smooth(y, box_pts):
    box = ones(box_pts)/box_pts
    y_smooth = convolve(y, box, mode='same')
    return y_smooth
