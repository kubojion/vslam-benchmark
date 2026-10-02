"""Geometry and support for the frozen ZED GNSS position reference.

No SLAM outputs are accepted by these functions. Angles describe the platform,
not the camera's downwards mounting angle. World axes are ENU.
"""
import numpy as np
from scipy.spatial.transform import Rotation


def retained_intervals(times, keep, maximum_gap_s=.5):
    times=np.asarray(times,dtype=float); keep=np.asarray(keep,dtype=bool)
    if times.ndim!=1 or keep.shape!=times.shape or np.any(np.diff(times)<=0):
        raise ValueError('expected increasing timestamps and a matching mask')
    selected=np.flatnonzero(keep)
    if not len(selected):raise ValueError('reference has no retained samples')
    split=np.flatnonzero((np.diff(selected)!=1) | (np.diff(times[selected])>maximum_gap_s))+1
    return [[float(times[a[0]]),float(times[a[-1]])] for a in np.split(selected,split)]


def enu_positions(lla, origin):
    """WGS84 geodetic degrees/metres to one fixed local ENU tangent plane."""
    lla=np.asarray(lla,dtype=float);origin=np.asarray(origin,dtype=float)
    def ecef(v):
        lat,lon=np.deg2rad(v[...,0]),np.deg2rad(v[...,1]);alt=v[...,2]
        n=6378137./np.sqrt(1-6.69437999014e-3*np.sin(lat)**2)
        return np.stack(((n+alt)*np.cos(lat)*np.cos(lon),(n+alt)*np.cos(lat)*np.sin(lon),
                         (n*(1-6.69437999014e-3)+alt)*np.sin(lat)),axis=-1)
    lat,lon=np.deg2rad(origin[:2]);r=np.array([[-np.sin(lon),np.cos(lon),0],
        [-np.sin(lat)*np.cos(lon),-np.sin(lat)*np.sin(lon),np.cos(lat)],
        [np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)]])
    return (ecef(lla)-ecef(origin))@r.T


def horizontal_lever():
    # Geometry document: physical forward differs from antenna heading by +1.53028 deg.
    # Camera yaw -1.40 deg relative to the raw antenna line -> +0.13028 deg to body.
    bias=np.arctan2(.037,1.385)
    mount=Rotation.from_euler('z',bias-np.deg2rad(1.4))*Rotation.from_euler('y',20.17,degrees=True)
    lens=np.array([2.86,0.,0.])+mount.apply([-.010,.060,.015])
    return lens[:2]


def camera_positions(antenna_enu, baseline_enu, *, antenna_above_camera_m=1.,
                     roll_deg=0., pitch_deg=0.):
    """Nominal level platform; pitch/roll perturbations are sensitivity controls.

    The primary reference uses heading alone, not SLAM or accelerometer attitude.
    1 m is the complete antenna-to-left-camera vertical separation; do not add
    internal camera offsets to it a second time.
    """
    baseline=np.asarray(baseline_enu,dtype=float)
    if baseline.ndim!=2 or baseline.shape[1]!=3 or not np.isfinite(baseline).all():
        raise ValueError('expected finite ENU baseline vectors')
    if np.any(np.linalg.norm(baseline[:,:2],axis=1)<.2):raise ValueError('invalid heading baseline')
    yaw=np.arctan2(baseline[:,1],baseline[:,0])-np.arctan2(.037,1.385)
    attitude=Rotation.from_euler('z',yaw)*Rotation.from_euler('y',pitch_deg,degrees=True)*Rotation.from_euler('x',roll_deg,degrees=True)
    lever=[*horizontal_lever(),-antenna_above_camera_m]
    return np.asarray(antenna_enu,dtype=float)+attitude.apply(lever)
