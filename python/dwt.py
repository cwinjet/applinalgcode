import random
from numpy import *
import matplotlib.pyplot as plt
from sound import *
from images import *
import scipy.io as sio
import os
import os.path




function x=dwt_impl(x, nres, wave_name, forward=True, dim=1, bd_mode=1, dual=False, transpose=False)
    % x:         Matrix whose DWT will be computed along the first dimension(s).      
    % nres:      Number of resolutions.
    % wave_name: Name of the wavelet.
    % forward:   Whether to apply the forward or reverse transform. Default: 1
    % dim:       The dimension of the transform (1 for sound, 2 for images). Default: 1
    % bd_mode:   Boundary extension mode. Default: 1
    % dual:      Whether to apply the dual wavelet rather than the wavelet itself. Default: 0
    % transpose: Whether the transpose is to be taken. Default: 0
    
    if transpose:
        forward = not forward
        dual = not dual
    if forward:
        f = findDWTKernel(wave_name, dual)
        if dim == 2:
            x = dwt2_impl(x, nres, f, bd_mode)
        elif dim == 1:
            x = dwt1_impl(x, nres, f, bd_mode)
    else:
        f = findIDWTKernel(wave_name, dual)
        if dim ==2:
            x = idwt2_impl(x, nres, f, bd_mode)
        elseif dim == 1:
            x = idwt1_impl(x, nres, f, bd_mode)


def dwt2_impl(X, nres, f, bd_mode):
    M, N = shape(X)[0:2]
    for res in range(nres):
        for n in range(0,N,2**res): 
            f(X[0::2**res, n], bd_mode)
        for m in range(0,M,2**res):
            f(X[m, 0::2**res], bd_mode)
    reorganize_coefficients2(X, nres, True)   
            
def idwt2_impl(X, nres, f, bd_mode):
    reorganize_coefficients2(X, nres, False)   
    M, N = shape(X)[0:2]        
    for res in range(nres - 1, -1, -1):
        for n in range(0, N, 2**res):
            f(X[0::2**res, n], bd_mode)
        for m in range(0, M, 2**res):
            f(X[m, 0::2**res], bd_mode)
  
def dwt1_impl(x, nres, f, bdmode):
    for res in range(nres):
        f(x[0::2**res], bd_mode)
    reorganize_coefficients(x, nres, True)
            
def idwt1_impl(x, nres, f, bd_mode):
    reorganize_coefficients(x, nres, False)
    for res in range(nres - 1, -1, -1):
        f(x[0::2**res], bd_mode)
        
        
        
        
        

def findDWTKernel(wave_name, dual):
    f = 0
    if dual:
        if wave_name.lower() =='cdf97':
            f = dwt_kernel_97_dual
        elif wave_name.lower() == 'cdf53':
            f = dwt_kernel_53_dual
        elif wave_name.lower() == 'pwl0':
            f = dwt_kernel_pwl0_dual
        elif wave_name.lower() == 'pwl2':
            f = dwt_kernel_pwl2_dual
        elif wave_name.lower() == 'haar':
            f = dwt_kernel_haar
        elif wave_name[:2].lower() == 'db' and not wave_name[-1].lower() =='x':
            vm = float(wave_name[2::])
            filters = getDBfilter(vm, 0)
            f = lambda x, bd_mode: dwt_kernel_ortho_dual(x, filters, bd_mode)
        elif wave_name[:2].lower() == 'db':
            vm = float(wave_name[2::-1])
            filters = liftingfactortho(vm, 0, 1)
            f = lambda x, bd_mode: dwt_kernel_ortho_dual(x, filters, bd_mode)
        elif wave_name[:3].lower() == 'sym' and not wave_name[-1].lower() =='x':
            vm = float(wave_name[3::])
            filters = getDBfilter(vm, 1)
            f = lambda x, bd_mode: det_kernel_ortho_dual(x, filters, bd_mode)
        elif wave_name[:3].lower() == 'sym':
            vm = float(wave_name[3::-1])
            filters = liftingfactortho(vm, 1, 1)
            f = lambda x, bd_mode: dwt_kernel_ortho_dual(x, filters, bd_mode)
    else:
        if wave_name.lower() =='cdf97':
            f = dwt_kernel_97
        elif wave_name.lower() == 'cdf53':
            f = dwt_kernel_53
        elif wave_name.lower() == 'pwl0':
            f = dwt_kernel_pwl0
        elif wave_name.lower() == 'pwl2':
            f = dwt_kernel_pwl2
        elif wave_name.lower() == 'haar':
            f = dwt_kernel_haar
        elif wave_name[:2].lower() == 'db' and not wave_name[-1].lower() =='x':
            vm = float(wave_name[2::])
            filters = getDBfilter(vm, 0)
            f = lambda x, bd_mode: dwt_kernel_ortho(x, filters, bd_mode)
        elif wave_name[:2].lower() == 'db':
            vm = float(wave_name[2::-1])
            filters = liftingfactortho(vm, 0, 1)
            f = lambda x, bd_mode: dwt_kernel_ortho(x, filters, bd_mode)
        elif wave_name[:3].lower() == 'sym' and not wave_name[-1].lower() =='x':
            vm = float(wave_name[3::])
            filters = getDBfilter(vm, 1)
            f = lambda x, bd_mode: dwt_kernel_ortho(x, filters, bd_mode)
        elif wave_name[:3].lower() == 'sym':
            vm = float(wave_name[3::-1])
            filters = liftingfactortho(vm, 1, 1)
            f = lambda x, bd_mode: dwt_kernel_ortho(x, filters, bd_mode)
    return f
    
def findIDWTKernel(wave_name, dual):
    f = 0
    if dual:
        if wave_name.lower() =='cdf97':
            f = idwt_kernel_97_dual
        elif wave_name.lower() == 'cdf53':
            f = idwt_kernel_53_dual
        elif wave_name.lower() == 'pwl0':
            f = idwt_kernel_pwl0_dual
        elif wave_name.lower() == 'pwl2':
            f = idwt_kernel_pwl2_dual
        elif wave_name.lower() == 'haar':
            f = idwt_kernel_haar
        elif wave_name[:2].lower() == 'db' and not wave_name[-1].lower() =='x':
            vm = float(wave_name[2::])
            filters = getDBfilter(vm, 0)
            f = lambda x, bd_mode: idwt_kernel_ortho_dual(x, filters, bd_mode)
        elif wave_name[:2].lower() == 'db':
            vm = float(wave_name[2::-1])
            filters = liftingfactortho(vm, 0, 1)
            f = lambda x, bd_mode: idwt_kernel_ortho_dual(x, filters, bd_mode)
        elif wave_name[:3].lower() == 'sym' and not wave_name[-1].lower() =='x':
            vm = float(wave_name[3::])
            filters = getDBfilter(vm, 1)
            f = lambda x, bd_mode: idwt_kernel_ortho_dual(x, filters, bd_mode)
        elif wave_name[:3].lower() == 'sym':
            vm = float(wave_name[3::-1])
            filters = liftingfactortho(vm, 1, 1)
            f = lambda x, bd_mode: idwt_kernel_ortho_dual(x, filters, bd_mode)
    else:
        if wave_name.lower() =='cdf97':
            f = idwt_kernel_97
        elif wave_name.lower() == 'cdf53':
            f = idwt_kernel_53
        elif wave_name.lower() == 'pwl0':
            f = idwt_kernel_pwl0
        elif wave_name.lower() == 'pwl2':
            f = idwt_kernel_pwl2
        elif wave_name.lower() == 'haar':
            f = IDWTKernelHaar
        elif wave_name[:2].lower() == 'db' and not wave_name[-1].lower() =='x':
            vm = float(wave_name[2::])
            filters = getDBfilter(vm, 0)
            f = lambda x, bd_mode: idwt_kernel_ortho(x, filters, bd_mode)
        elif wave_name[:2].lower() == 'db':
            vm = float(wave_name[2::-1])
            filters = liftingfactortho(vm, 0, 1)
            f = lambda x, bd_mode: idwt_kernel_ortho(x, filters, bd_mode)
        elif wave_name[:3].lower() == 'sym' and not wave_name[-1].lower() =='x':
            vm = float(wave_name[3::])
            filters = getDBfilter(vm, 1)
            f = lambda x, bd_mode: idwt_kernel_ortho(x, filters, bd_mode)
        elif wave_name[:3].lower() == 'sym':
            vm = float(wave_name[3::-1])
            filters = liftingfactortho(vm, 1, 1)
            f = lambda x, bd_mode: idwt_kernel_ortho(x, filters, bd_mode)
    return f

def getDBfilter(vm, type):
    filter = 0;
    dest = 'var'
    if (type == 0):
        filename = '%s/DB%d.mat' % (dest, vm)
    else:
        filename = '%s/sym%d.mat' % (dest, vm)

    if os.path.isfile(filename):
        sio.loadmat(filename)
    else:
        filter = liftingfactortho(vm, type)
        
        if not os.path.isdir(dest):
            os.mkdir(dest)
        
        sio.savemat(filename, {'filter': filter})
    return filter


def DWTKernelFilters(H0, H1, G0, G1, x, bd_mode, dual):
    f0, f1 = H0, H1
    if dual:
        f0, f1 = G0, G1
    N = len(x)
    x0 = x.copy()
    x1 = x.copy()
    filterS(f0, x0, bd_mode)
    filterS(f1, x1, bd_mode)
    x[::2] = x0[::2]
    x[1::2] = x1[1::2]

def IDWTKernelFilters(H0, H1, G0, G1, x, bd_mode, dual):
    f0, f1 = G0, G1
    if dual:
        f0, f1 = H0, H1
    N = len(x)
    x0 = x.copy(); x0[1::2] = 0
    x1 = x.copy(); x1[::2] = 0
    filterS(f0, x0, bd_mode)
    filterS(f1, x1, bd_mode)
    x[:] = x0 + x1
        
def reorganize_coefficients(x, nres, forward):
    """
    Permute one-dimensional DWT coefficients from the order used in-place DWT, to the order with low resolution coordinates first, as required by the DWT. If forward is false, the opposite reorganization is used. 
    
    x: The vector which holds the DWT coefficients. The reorganization is formed in the first dimension, but x may have a second dimension, as is the case for sound with more than one channel. 
    nres: The number of resolutions in x.
    forward: If forward is True, reorganize from in-place order to DWT coefficient order. If forward is False, reorganize from DWT coefficient order to in-place order.
    """
    N = shape(x)[0]
    y = zeros_like(x)
    sz = shape(x[0::2**nres])[0]
    if forward:
        y[0:sz] = x[0::2**nres]
    else:
        y[0::2**nres] = x[0:sz]
    for res in range(nres, 0, -1):
        lw = shape(x[2**(res - 1)::2**res])[0]
        if forward:
            y[sz:(sz + lw)] = x[2**(res - 1)::2**res]
        else:
            y[2**(res - 1)::2**res] = x[sz:(sz + lw)]
        sz += lw
    x[:] = y[:]
    
def reorganize_coefficients2(X, nres, forward):
    """
    Permute two-dimensional DWT coefficients from the order used in-place DWT, to the order with low resolution coordinates first, as required by the DWT. If forward is false, the opposite reorganization is used. 
    
    X: The matrix which holds the DWT coefficients. The reorganization is formed in the two first dimensions, but X may have a third dimension, as is the case for images with more than one colour component. 
    nres: The number of resolutions in X.
    forward: If forward is True, reorganize from in-place order to DWT coefficient order. If forward is False, reorganize from DWT coefficient order to in-place order.
    """
    M, N = shape(X)[0:2]
    Y = zeros_like(X)
    lc1, lc2 = shape(X[0::2**nres, 0::2**nres])[0:2]
    if forward:
        Y[0:lc1, 0:lc2] = X[0::2**nres, 0::2**nres]
    else:
        Y[0::2**nres, 0::2**nres] = X[0:lc1, 0:lc2]
    for res in range(nres, 0, -1):
        lw1, lw2 = shape(X[2**(res - 1)::2**res, 2**(res - 1)::2**res])[0:2]
        if forward:
            Y[lc1:(lc1 + lw1), 0:lc2] = X[2**(res - 1)::2**res, 0::2**res]
            Y[lc1:(lc1 + lw1), lc2:(lc2 + lw2)] = X[2**(res - 1)::2**res, 2**(res - 1)::2**res]
            Y[0:lc1, lc2:(lc2 + lw2)] = X[0::2**res, 2**(res - 1)::2**res]
        else:
            Y[2**(res - 1)::2**res, 0::2**res] = X[lc1:(lc1 + lw1), 0:lc2]
            Y[2**(res - 1)::2**res, 2**(res - 1)::2**res] = X[lc1:(lc1 + lw1), lc2:(lc2 + lw2)]
            Y[0::2**res, 2**(res - 1)::2**res] = X[0:lc1, lc2:(lc2 + lw2)]
        lc1 += lw1
        lc2 += lw2
    X[:] = Y[:]
      
# Generic DWT/IDWT implementations


            
# Lifting steps
            
def liftingstepevensymm(lmbda, x, bd_mode):
    """
    Apply an elementary symmetric lifting step of even type to x. 
    
    lmbda: The common value of the two filter coefficients
    x: The vector which we apply the lifting step to
    bd_mode: Whether to apply symmetric extension to the input
    """
    if (not bd_mode) and mod(len(x), 2)!=0:
        raise AssertionError()
    if bd_mode:
        x[0] += 2*lmbda*x[1] # With symmetric extension
    else:
        x[0] += lmbda*(x[1]+x[-1])
    x[2:-1:2] += lmbda*(x[1:-2:2] + x[3::2])
    if mod(len(x), 2)==1 and bd_mode:
        x[-1] += 2*lmbda*x[-2] # With symmetric extension
  
def liftingstepoddsymm(lmbda, x, bd_mode):
    """
    Apply an elementary symmetric lifting step of odd type to x. 
    
    lmbda: The common value of the two filter coefficients
    x: The vector which we apply the lifting step to
    bd_mode: Whether to apply symmetric extension to the input
    """
    if (not bd_mode) and mod(len(x), 2)!=0:
        raise AssertionError()
    x[1:-1:2] += lmbda*(x[0:-2:2] + x[2::2])
    if mod(len(x), 2)==0:
        if bd_mode:
            x[-1] += 2*lmbda*x[-2] # With symmetric extension
        else:
            x[-1] += lmbda*(x[0]+x[-2])

def liftingstepeven(lmbda1, lmbda2, x):
    """
    Apply an elementary non-symmetric lifting step of even type to x.
    
    lmbda1: The first filter coefficient
    lmbda2: The second filter coefficient
    x: The vector which we apply the lifting step to
    """
    if mod(len(x), 2)!=0:
        raise AssertionError()
    x[0] += lmbda1*x[1] + lmbda2*x[-1]
    x[2:-1:2] += lmbda1*x[3::2] + lmbda2*x[1:-2:2]
            
def liftingstepodd(lmbda1, lmbda2, x):
    """
    Apply an elementary non-symmetric lifting step of odd type to x.
    
    lmbda1: The first filter coefficient
    lmbda2: The second filter coefficient
    x: The vector which we apply the lifting step to
    """
    if mod(len(x), 2)!=0:
        raise AssertionError()
    x[1:-2:2] += lmbda1*x[2:-1:2] + lmbda2*x[0:-3:2]
    x[-1] += lmbda1*x[0] + lmbda2*x[-2]                                                

# The Haar wavelet

def dwt_kernel_haar(x, bd_mode):
    x /= sqrt(2)
    if mod(len(x), 2)==1:
        a, b = x[0] + x[1] - x[-1], x[0] - x[1] - x[-1]
        x[0], x[1] = a, b 
        x[-1] *= 2
    else:
        a, b = x[0] + x[1], x[0] - x[1] 
        x[0], x[1] = a, b 
    for k in range(2,len(x) - 1,2):
        a, b = x[k] + x[k+1], x[k] - x[k+1]  
        x[k], x[k+1] = a, b 
         
def idwt_kernel_haar(x, bd_mode):
    x /= sqrt(2)
    if mod(len(x), 2)==1:
        a, b = x[0] + x[1]  + x[-1], x[0] - x[1]
        x[0], x[1] = a, b
        for k in range(2,len(x) - 2, 2):
            a, b = x[k] + x[k+1], x[k] - x[k+1] 
            x[k], x[k+1] = a, b 
    else:    
        for k in range(0,len(x) - 1, 2):
            a, b = x[k] + x[k+1], x[k] - x[k+1] 
            x[k], x[k+1] = a, b   
            
# Piecewise linear wavelets

def dwt_kernel_pwl0_dual(x, bd_mode):
    x /= sqrt(2)
    liftingstepevensymm(0.5, x, bd_mode)
        
def dwt_kernel_pwl0(x, bd_mode):
    x *= sqrt(2)
    liftingstepoddsymm(-0.5, x, bd_mode)
        
def idwt_kernel_pwl0_dual(x, bd_mode):
    x *= sqrt(2)
    liftingstepevensymm(-0.5, x, bd_mode)
        
def idwt_kernel_pwl0(x, bd_mode):
    x /= sqrt(2)
    liftingstepoddsymm(0.5, x, bd_mode)

def dwt_kernel_pwl2_dual(x, bd_mode):
    liftingstepevensymm(0.5, x, bd_mode)
    liftingstepoddsymm(-0.25, x, bd_mode)
    x /= sqrt(2)
    
def dwt_kernel_pwl2(x, bd_mode):
    liftingstepoddsymm(-0.5, x, bd_mode)
    liftingstepevensymm(0.25, x, bd_mode)
    x *= sqrt(2)
    
def idwt_kernel_pwl2_dual(x, bd_mode):
    x *= sqrt(2)
    liftingstepoddsymm(0.25, x, bd_mode)
    liftingstepevensymm(-0.5, x, bd_mode)
    
def idwt_kernel_pwl2(x, bd_mode):
    x /= sqrt(2)
    liftingstepevensymm(-0.25, x, bd_mode)
    liftingstepoddsymm(0.5, x, bd_mode)       
                
        
# JPEG2000-related wavelet kernels
        
def dwt_kernel_53_dual(x, bd_mode):
    x[0::2] *= 0.5
    x[1::2] *= 2
    liftingstepevensymm(0.125, x, bd_mode)
    liftingstepoddsymm(-1, x, bd_mode)
    
def dwt_kernel_53(x, bd_mode):
    x[0::2] *= 2
    x[1::2] *= 0.5
    liftingstepoddsymm(-0.125, x, bd_mode)
    liftingstepevensymm(1, x, bd_mode)
            
def idwt_kernel_53_dual(x, bd_mode):
    liftingstepoddsymm(1, x, bd_mode)
    liftingstepevensymm(-0.125, x, bd_mode)     
    x[0::2] *= 2
    x[1::2] *= 0.5
    
def idwt_kernel_53(x, bd_mode):
    liftingstepevensymm(-1, x, bd_mode)
    liftingstepoddsymm(0.125, x, bd_mode)     
    x[0::2] *= 0.5
    x[1::2] *= 2


def dwt_kernel_97_dual(x, bd_mode):
    lambda1=-0.586134342059950
    lambda2=-0.668067171029734
    lambda3=0.070018009414994
    lambda4=1.200171016244178
    alpha=-1.149604398860250
    beta=-0.869864451624777
    
    x[0::2] /= alpha
    x[1::2] /= beta
    liftingstepevensymm(lambda4, x, bd_mode)
    liftingstepoddsymm(lambda3, x, bd_mode)
    liftingstepevensymm(lambda2, x, bd_mode)
    liftingstepoddsymm(lambda1, x, bd_mode)
        
def dwt_kernel_97(x, bd_mode):
    lambda1=-0.586134342059950
    lambda2=-0.668067171029734
    lambda3=0.070018009414994
    lambda4=1.200171016244178
    alpha=-1.149604398860250
    beta=-0.869864451624777
    
    x[0::2] *= alpha
    x[1::2] *= beta
    liftingstepoddsymm(-lambda4, x, bd_mode)
    liftingstepevensymm(-lambda3, x, bd_mode)
    liftingstepoddsymm(-lambda2, x, bd_mode)
    liftingstepevensymm(-lambda1, x, bd_mode)
                
def idwt_kernel_97_dual(x, bd_mode):
    lambda1=-0.586134342059950
    lambda2=-0.668067171029734
    lambda3=0.070018009414994
    lambda4=1.200171016244178
    alpha=-1.149604398860250
    beta=-0.869864451624777
    
    liftingstepoddsymm(-lambda1, x, bd_mode)
    liftingstepevensymm(-lambda2, x, bd_mode)   
    liftingstepoddsymm(-lambda3, x, bd_mode)
    liftingstepevensymm(-lambda4, x, bd_mode)      
    x[0::2] *= alpha
    x[1::2] *= beta

def idwt_kernel_97(x, bd_mode):
    lambda1=-0.586134342059950
    lambda2=-0.668067171029734
    lambda3=0.070018009414994
    lambda4=1.200171016244178
    alpha=-1.149604398860250
    beta=-0.869864451624777
        
    liftingstepevensymm(lambda1, x, bd_mode)
    liftingstepoddsymm(lambda2, x, bd_mode)   
    liftingstepevensymm(lambda3, x, bd_mode)
    liftingstepoddsymm(lambda4, x, bd_mode)      
    x[0::2] /= alpha
    x[1::2] /= beta
        
# Orthonormal wavelets
        
def dwt_kernel_ortho_dual( x, bd_mode):
    global lambdas, alpha, beta
    global beta
    
    x[0::2] /= alpha
    x[1::2] /= beta
    for stepnr in range(lambdas.shape[0] - 1, 0, -2):
        liftingstepodd(lambdas[stepnr, 1], lambdas[stepnr, 0], x)
        liftingstepeven(lambdas[stepnr -1, 1], lambdas[stepnr - 1, 0], x)   
    if mod(lambdas.shape[0], 2)==1:
        liftingstepodd(lambdas[0, 1], lambdas[0, 0], x)

def dwt_kernel_ortho( x, bd_mode):
    global lambdas, alpha, beta
    global beta
    
    x[0::2] *= alpha
    x[1::2] *= beta
    for stepnr in range(lambdas.shape[0] - 1, 0, -2):
        liftingstepeven(-lambdas[stepnr, 0], -lambdas[stepnr, 1], x)
        liftingstepodd(-lambdas[stepnr - 1, 0], -lambdas[stepnr - 1, 1], x)  
    if mod(lambdas.shape[0], 2)==1:
        liftingstepeven(-lambdas[0, 0], -lambdas[0, 1], x)
  
def idwt_kernel_ortho_dual( x, bd_mode):
    global lambdas
    global alpha
    global beta

    stepnr = 0
    if mod(lambdas.shape[0], 2) == 1: # Start with an odd step
        liftingstepodd(-lambdas[stepnr, 1], -lambdas[stepnr, 0], x)
        stepnr += 1
    while stepnr < lambdas.shape[0]:
        liftingstepeven(-lambdas[stepnr, 1], -lambdas[stepnr, 0], x)
        liftingstepodd(-lambdas[stepnr + 1, 1], -lambdas[stepnr + 1, 0], x)
        stepnr += 2
    x[0::2] *= alpha
    x[1::2] *= beta
    
def idwt_kernel_ortho( x, bd_mode):
    global lambdas
    global alpha
    global beta
    
    stepnr = 0
    if mod(lambdas.shape[0],2) == 1: # Start with an even step
        liftingstepeven(lambdas[stepnr, 0], lambdas[stepnr, 1], x)
        stepnr += 1
    while stepnr < lambdas.shape[0]:
        liftingstepodd(lambdas[stepnr, 0], lambdas[stepnr, 1], x)
        liftingstepeven(lambdas[stepnr + 1, 0], lambdas[stepnr + 1, 1], x)
        stepnr += 2
    x[0::2] /= alpha
    x[1::2] /=beta
            



# testcode




def h0h1computeortho(N):
    vals = computeQN(N)
    rts=roots(vals)
    rts1=rts[nonzero(abs(rts)>1)]
    g0=array([1])
    for rt in rts1:
        g0=convolve(g0,[-rt,1])
    
    K=sqrt(vals[0]*(-1)**(len(rts1))/prod(rts1))
    g0=K*g0
    for k in range(N):
        g0=convolve(g0,[1/2.,1/2.])
    
    g0=real(g0)
    h0=g0[::-1]
    g1=g0[::-1]*(-1)**(array(range(len(g0))))
    h1=g1[::-1]
    return h0, h1

def liftingfactortho(N, type=0, debug_mode=False):
    """
    Assume that len(h1)==len(h0), and that h0 and h1 are even length and as symmetric as possible, with h0 with a minimum possible overweight of filter coefficients to the left, h1 to the right
    This function computes lifting steps l1, l2,...,ln, and constants alpha, beta so that ln ... l2 l1 H =  diag(alpha,beta), and stores these as global variables
    This gives the following recipes for 
        Computing H: first multiply with diag(alpha,beta), then the inverses of the lifting steps in reverse order 
        Computing G: apply the lifting steps in the order given, finally multiply with diag(1/alpha,1/beta)
    ln is always odd, so that l1 is odd if and only if n is odd.
    All even lifting steps have only filter coefficients 0,1. All odd lifting steps have only filter coefficients -1,0
    """
    global lambdas, alpha, beta
    h0, h1 = h0h1computeortho(N)
    stepnr=0
    start1, end1, len1, start2, end2, len2 = 0, len(h0)/2-1, len(h0)/2,  0, len(h1)/2-1, len(h1)/2
    lambdas=zeros((len1+1,2))
    if mod(len1,2)==0: # Start with an even step
        h00, h01 = h0[0:len(h0):2], h0[1:len(h0):2]
        h10, h11 = h1[0:len(h1):2], h1[1:len(h1):2]
  
        lambda1=-h00[0]/h10[0]
        h00=h00+lambda1*h10 
        h01=h01+lambda1*h11
        start1, end1, len1 = 1, len1-1, len1-1
        lambdas[stepnr,:] = [lambda1,0]
    else: # Start with an odd step
        h00, h01 = h0[1:len(h0):2], h0[0:len(h0):2]
        h10, h11 = h1[1:len(h1):2], h1[0:len(h1):2]
    
        lambda1=-h10[end1]/h00[end1] 
        h10=h10+lambda1*h00 
        h11=h11+lambda1*h01
        start2, end2, len2 = 0, len2 - 2, len2-1
        lambdas[stepnr,:] = [0,lambda1]
  
    #[h00 h01; h10 h11]
    #convolve(h00,h11)-convolve(h10,h01)
    stepnr=stepnr+1

    # print [h00 h01; h10 h11], convolve(h00,h11)-convolve(h10,h01)
    while len2>0: # Stop when the second element in the first column is zero
        if len1>len2: # Reduce the degree in the first row. 
            lambda1=-h00[start1]/h10[start2]
            lambda2=-h00[end1]/h10[end2]
            h00[start1:(end1+1)] = h00[start1:(end1+1)]+convolve(h10[start2:(end2+1)],[lambda1,lambda2])
            h01[start1:(end1+1)] = h01[start1:(end1+1)]+convolve(h11[start2:(end2+1)],[lambda1,lambda2])
            start1, end1, len1 = start1+1, end1-1, len1-2
        else: # reduce the degree in the second row. 
            lambda1=-h10[start2]/h00[start1]
            lambda2=-h10[end2]/h00[end1]
            h10[start2:(end2+1)] = h10[start2:(end2+1)]+convolve(h00[start1:(end1+1)],[lambda1,lambda2])
            h11[start2:(end2+1)] = h11[start2:(end2+1)]+convolve(h01[start1:(end1+1)],[lambda1,lambda2])
            start2, end2, len2 = start2+1, end2-1, len2-2
        lambdas[stepnr,:]=[lambda1,lambda2]
        stepnr=stepnr+1
    
    # print [h00 h01; h10 h11], convolve(h00,h11)-convolve(h10,h01)
  
    # Add the final lifting, and compute alpha,beta
    alpha=sum(h00)
    beta=sum(h11)
    lastlift=-sum(h01)/beta
    if mod(len(h0)/2,2)==0:
        lambdas[stepnr,:] = [0,lastlift]
    else:
        lambdas[stepnr,:] = [lastlift,0]
    # [h00 h01; h10 h11]
    
def computeQN(N):
    """
    Compute the coefficients of the polynomial Q^(N)((1-cos(w))/2).
    """
    QN=zeros(N)
    for k in range(N):
        QN[k] = 2*math.factorial(N+k-1)/(math.factorial(k)*math.factorial(N-1))
    vals = array([QN[0]])
    start = array([1.0])
    for k in range(1,N):
        start = convolve(start,[-1/4.0,1/2.0,-1/4.0])
        vals = hstack([0,vals])
        vals = hstack([vals,0])
        vals = vals + QN[k]*start
    return vals
    
    
    
def h0h1compute97():
    QN = computeQN(4)
    
    rts = roots(QN)
    rts1 = rts[nonzero(abs(imag(rts))>0.001)] # imaginary roots
    rts2 = rts[nonzero(abs(imag(rts))<0.001)] # real roots
    
    h0=array([1])
    for rt in rts1:
        h0 = convolve(h0, [-rt,1])
    for k in range(2):
        h0 = convolve(h0,[1/4.,1/2.,1/4.])
    h0=h0*QN[0]
    
    g0=array([1])
    for rt in rts2:
        g0 = convolve(g0, [-rt,1])
    for k in range(2):
        g0 = convolve(g0,[1/4.,1/2.,1/4.])
    
    g0, h0 = real(g0), real(h0)
    x = sqrt(2)/abs(sum(h0))
    g0, h0 = g0/x, h0*x
    N= g0.shape[0]
    h1=g0*(-1)**(array(range(-(N-1)/2,(N+1)/2)))
    N= h0.shape[0]
    g1=h0*(-1)**(array(range(-(N-1)/2,(N+1)/2)))
    #print h0, h1, g0, g1
    return h0, h1
  
def liftingfact97():
    h0, h1 = h0h1compute97() # Should have 9 and 7 filter coefficients.
    h00, h01 = h0[0:9:2], h0[1:9:2]
    h10, h11 = h1[0:7:2], h1[1:7:2]
    
    lambdas=zeros(4)
    
    lambdas[0] = -h00[0]/h10[0]
    h00[0:5] = h00[0:5]+convolve(h10[0:4],[lambdas[0],lambdas[0]])
    h01[0:4] = h01[0:4]+convolve(h11[0:3],[lambdas[0],lambdas[0]])  
    
    lambdas[1] = -h10[0]/h00[1]
    h10[0:4] = h10[0:4]+convolve(h00[1:4],[lambdas[1],lambdas[1]])
    h11[0:3] = h11[0:3]+convolve(h01[1:3],[lambdas[1],lambdas[1]]) 
    
    lambdas[2] = -h00[1]/h10[1]
    h00[1:4] = h00[1:4]+convolve(h10[1:3],[lambdas[2],lambdas[2]])
    h01[1:3] = h01[1:3]+convolve(h11[1:2],[lambdas[2],lambdas[2]])  
    
    lambdas[3] = -h10[1]/h00[2]
    h10[0:4] = h10[0:4]+convolve(h00[1:4],[lambdas[3],lambdas[3]])
    h11[0:3] = h11[0:3]+convolve(h01[1:3],[lambdas[3],lambdas[3]]) 
    
    alpha, beta = h00[2], h11[1] 
    return lambdas, alpha, beta    
    
def _test_kernel(wave_name):
    print 'Testing %s, 1D' % wave_name
    res = random.random(16)
    x = zeros(16)
    x[:] = res[:]
    dwt_impl(x,2,wave_name)
    dwt_impl(x,2,wave_name, False)
    diff = abs(x-res).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
    print 'Testing %s, 2D' % wave_name
    res = random.random((16,2))
    x = zeros((16,2))
    x[:] = res[:]
    dwt_impl(x,2,wave_name)
    dwt_impl(x,2,wave_name, False)
    diff = abs(x-res).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
def _test_kernel_ortho():
    print 'Testing orthonormal wavelets'
    res = random.random(16) # only this assumes that N is even
    x = zeros(16)
    
    print 'Testing that the reverse inverts the forward transform'
    x[0:16] = res[0:16]
    dwt_impl(x, 2, 'db4x')
    dwt_impl(x, 2, 'db4x', False)
    diff = max(abs(x-res))
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
    print 'Testing that the transform is orthogonal, i.e. that the transform and its dual are equal'
    x[0:16] = res[0:16]
    dwt_impl(x, 2, 'db4x')
    dwt_impl(res, 2, 'db4x', True, 1, 0, True)
    diff = max(abs(x-res))
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
def _test_dwt_different_sizes():
    print 'Testing the DWT on different input sizes'
    m = 4

    print 'Testing the DWT for greyscale image'
    img = random.random((32,32))
    img2 = zeros_like(img)
    img2[:] = img[:]
    dwt_impl(img2, m, 'cdf97', True, 2)
    dwt_impl(img2, m, 'cdf97', False, 2)
    diff = abs(img2-img).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
    print 'Testing the DWT for RGB image'
    img = random.random((32, 32, 3))
    img2 = zeros_like(img)
    img2[:] = img[:]
    dwt_impl(img2, m, 'cdf97', True, 2)
    dwt_impl(img2, m, 'cdf97', False, 2)
    diff = abs(img2-img).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
    print 'Testing the DWT for sound with one channel'
    sd = random.random(32)
    sd2 = zeros_like(sd)
    sd2[:] = sd[:]
    dwt_impl(sd2, m, 'cdf97')
    dwt_impl(sd2, m, 'cdf97', False)
    diff = abs(sd2-sd).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
    print 'Testing the DWT for sound with two channels'
    sd = random.random((32,2))
    sd2 = zeros_like(sd)
    sd2[:] = sd[:]
    dwt_impl(sd2, m, 'cdf97')
    dwt_impl(sd2, m, 'cdf97', False)
    diff = abs(sd2-sd).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
def _test_orthogonality():
    print 'Testing that the wavelet and the dual wavelet are equal for orthonormal wavelets'
    x0 = random.random(32)
    
    print 'Testing that the IDWT inverts the DWT'
    x = x0.copy()
    dwt_impl(x, 2, 'db4x', True, 1, 0, False)
    dwt_impl(x, 2, 'db4x', False, 1, 0, False);
    diff = abs(x-x0).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff
    
    print 'Apply the transpose, to see that the transpose equals the inverse'
    x = x0.copy()
    dwt_impl(x, 2, 'db4x', True, 1, 0, False)
    dwt_impl(x, 2, 'db4x', False, 1, 0, True)
    diff = abs(x-x0).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff

    print 'To see this at the level of kernel transformations'
    x = x0.copy()
    dwt_kernel_ortho(x, 0) # TODO
    idwt_kernel_ortho_dual(x, 0)
    diff = abs(x-x0).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff

    print 'See that the wavelet transform equals the dual wavelet transform'
    x = x0.copy()
    dwt_impl(x, 2, 'db4x', True, 1, 0, True)
    dwt_impl(x0, 2, 'db4x', True, 1, 0, False)
    diff = abs(x-x0).max()
    assert diff < 1E-13, 'bug, diff=%s' % diff



if __name__=='__main__':
    _test_dwt_different_sizes()
    _test_kernel_ortho()
    _test_orthogonality()
    _test_kernel( 'cdf97')
    _test_kernel( 'cdf53')
    _test_kernel( 'pwl0')
    _test_kernel( 'pwl2')
    _test_kernel( 'haar')