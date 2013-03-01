import scipy as sc
from scipy.linalg import eigh
import code

def delta(kx,ky,param):
    return 0.5*(sc.cos(kx*2*sc.pi)*sc.exp(1j*param[0]*sc.pi)\
            +sc.cos(ky*2*sc.pi)*sc.exp(-1j*param[0]*sc.pi))

def omega(kx,ky,param):
    return sc.sqrt(param[1]**2+abs(delta(kx,ky,param))**2)

def uk(kx,ky,spin,band,param):
    if band==-1:
        return sc.sqrt(0.5*(1+spin*param[1]/omega(kx,ky,param)))
    else:
        return  -sc.conj(delta(kx,ky,param))/abs(delta(kx,ky,param))\
                *sc.sqrt(0.5*(1-spin*param[1]/omega(kx,ky,param)))

def vk(kx,ky,spin,band,param):
    if band==-1:
        return  delta(kx,ky,param)/abs(delta(kx,ky,param))*\
                sc.sqrt(0.5*(1-spin*param[1]/omega(kx,ky,param)));
    else:
        return sc.sqrt(0.5*(1+spin*param[1]/omega(kx,ky,param)));

def phiktrans(kx,ky,qx,qy,p,r=sc.array([0,0])):
    kqx=kx-qx
    kqy=ky-qy
    if sc.mod(sc.sum(r),2)==0:
        return  sc.exp(-2j*sc.pi*(kx*r[0]+ky*r[1]))*(\
                sc.conj(uk(kx,ky,1,1,p))*uk(kqx,kqy,-1,-1,p)+\
                sc.conj(vk(kx,ky,1,1,p))*vk(kqx,kqy,-1,-1,p))
    if sc.mod(sc.sum(r),2)==1:
        return sc.exp(-2j*sc.pi*(kx*r[0]+ky*r[1]))*(\
                sc.conj(vk(kx,ky,1,1,p))*uk(kqx,kqy,-1,-1,p)+\
                sc.conj(uk(kx,ky,1,1,p))*vk(kqx,kqy,-1,-1,p))

def phiklong(kx,ky,qx,qy,spin,p):
    kqx=kx-qx
    kqy=ky-qy
    return 0.5*spin*(sc.conj(uk(kx,ky,spin,1,p))*uk(kqx,kqy,spin,-1,p)+\
                     sc.conj(vk(kx,ky,spin,1,p))*vk(kqx,kqy,spin,-1,p))

def fermisea(Lx,Ly,shift):
    fskx=sc.zeros(Lx*Ly/2)
    fsky=sc.zeros(Lx*Ly/2)
    i=0
    for kx in range(Lx):
        for ky in range(Ly):
            if inmbz(float(kx+shift[0])/Lx,float(ky+shift[1])/Ly):
                fskx[i]=float(kx+shift[0])/Lx
                fsky[i]=float(ky+shift[1])/Ly
                i+=1
    return fskx,fsky

def inmbz(kx,ky):
    fkx=fold(kx)
    fky=fold(ky)
    tol=1e-6
    return (fky<=-0.5+fkx+tol) + (fky< 0.5-fkx-tol)\
            + (fky>=1.5-fkx-tol) + (fky>0.5+fkx+tol)

def fold(k):
    return k-((k<0) + (k>=1))*sc.floor(k)

def mbzmod(kx,ky):
    mkx=fold(kx)
    mky=fold(ky)
    mmkx=fold(mkx+0.5*(1-inmbz(mkx,mky)))
    mmky=fold(mky+0.5*(1-inmbz(mkx,mky)))
    return mmkx,mmky

def transfermisigns(Lx,Ly,shift,q):
    kx,ky=fermisea(Lx,Ly,shift)
    kqx=sc.mod(kx*Lx-shift[0]-q[0]*Lx,Lx)/Lx+shift[0]/Lx
    kqy=sc.mod(ky*Ly-shift[1]-q[1]*Ly,Ly)/Ly+shift[1]/Ly
    kqx,kqy=mbzmod(kqx,kqy)
    fsign=sc.zeros(len(kx))
    gsup=sc.zeros(2*len(kx))
    gsup[0::2]=1
    gsdo=sc.zeros(2*len(kx))
    gsdo[0::2]=1
    for k in range(len(kx)):
        ma=abs(kqx[k]-kx)+abs(kqy[k]-ky)
        ma=(ma==sc.amin(ma))
        idx=sc.arange(0,len(ma),1)[ma]
        fsign[k]=(-1)**sum(gsdo[0:2*idx])*(-1)**sum(gsup[0:(2*k+1)])
    return fsign

def longfermisigns(Lx,Ly,shift,q):
    kx,ky=fermisea(Lx,Ly,shift)
    kqx=sc.mod(kx*Lx-shift[0]-q[0]*Lx,Lx)/Lx+shift[0]/Lx
    kqy=sc.mod(ky*Ly-shift[1]-q[1]*Ly,Ly)/Ly+shift[1]/Ly
    kqx,kqy=mbzmod(kqx,kqy)
    fsign=sc.zeros(2*len(kx))
    if (abs(q[0])+abs(q[1]))<1e-6 or (abs(q[0]-0.5)+abs(q[1]-0.5))<1e-6:
        fsign=sc.zeros(2*len(kx)+1)
        fsign[-1]=1
    for k in range(len(kx)):
        gsup=sc.zeros(2*len(kx))
        gsup[0::2]=1
        ma=abs(kqx[k]-kx)+abs(kqy[k]-ky)
        ma=(ma==sc.amin(ma))
        idx=sc.arange(0,len(ma),1)[ma]
        fsign[2*k]=(-1)**sum(gsup[0:2*idx])
        gsup[2*idx]=0
        fsign[2*k]*=(-1)**sum(gsup[0:(2*k+1)])
        fsign[2*k+1]=fsign[2*k]
    return fsign

def fixfermisigns(Lx,Ly,shift,q,H,O,ori):
    fs=[]
    if ori=='trans':
        fs=transfermisigns(Lx,Ly,shift,q)
    elif ori=='long':
        fs=longfermisigns(Lx,Ly,shift,q)
    H=sc.dot(sc.diag(fs),sc.dot(H,sc.diag(fs)))
    O=sc.dot(sc.diag(fs),sc.dot(O,sc.diag(fs)))
    return H,O

def sqwtransamp(H,O,Lx,Ly,q,shift,phi,neel):
    kx,ky=fermisea(Lx,Ly,shift)
    E,V=eigh(H,O)
    pk=phiktrans(kx,ky,q[0],q[1],[phi,neel])
    sqw=abs(sc.einsum('ij,ik,k',sc.conj(V),O,pk))**2
    return E,sqw

def sqwlongamp(H,O,Lx,Ly,q,shift,phi,neel):
    kx,ky=fermisea(Lx,Ly,shift)
    E,V=eigh(H,O)
    sqw=len(E)*[0]
    for e in range(len(E)):
        pkup=sc.resize(phiklong(kx,ky,q[0],q[1],1,[phi,neel]),(len(kx),1))
        pkdo=sc.resize(phiklong(kx,ky,q[0],q[1],-1,[phi,neel]),(len(kx),1))
        pk=sc.zeros((2*len(pkup),1),complex)
        pk[0:2*len(pkup):2]=pkup
        pk[1:2*len(pkup):2]=pkdo
        if (abs(q[0])+abs(q[1]))<1e-6 or\
           (abs(q[0]-0.5)+abs(q[1]-0.5))<1e-6:
            pk.append([0])
            if neel!=0:
                pk[-1]=sc.sum(neel/omega(kx,ky,p))
        sqw[e]=abs(sc.dot(sc.conj(V[:,e]),sc.dot(O,pk)))**2
    return E,sqw

def transspinon(H,O,Lx,Ly,q,shift,phi,neel,rs,t):
    kx,ky=fermisea(Lx,Ly,shift)
    E,V=eigh(H,O)
    Wq=sc.zeros((sc.shape(rs)[0],len(t)))
    pk=phiktrans(kx,ky,q[0],q[1],[phi,neel])
    rhs=sc.dot(sc.conj(V.T),sc.dot(O,pk))
    for i in range(sc.shape(rs)[0]):
        pkr=phiktrans(kx,ky,q[0],q[1],[phi,neel],r=rs[i,:])
        lhs=sc.dot(sc.conj(pkr),sc.dot(O,V))
        omt=sc.exp(1j*sc.einsum('i,j',t,E))
        omt=sc.einsum('ij,kj->kij',sc.eye(len(E)),omt)
        Wq[i,:]=abs(sc.einsum('i,kij,j',lhs,omt,rhs))**2
    return Wq

def gaussians(x,x0,A,sig):
    gg=sc.zeros(sc.shape(x))
    for p in range(len(x0)):
        gg+=A[p]*sc.sqrt(1/(2*sc.pi))/sig[p]*sc.exp(-0.5*(x-x0[p])**2/sig[p]**2)
    return gg

def Renorm(sqsq,O,Lx,Ly,q,shift,p):
    kx,ky=fermisea(Lx,Ly,shift)
    pp=phiktrans(kx,ky,float(q[0])/Lx,float(q[1])/Ly,[p['phi'],p['neel']])
    b=sc.dot(sc.conj(pp),sc.dot(O,pp))
    r=sqsq/b
    if sc.isnan(r):
        r=1
    return r,b

if __name__=='__main__':
    pass
