#!/usr/bin/env python3
"""Generate report-only vector figures from audited source and closed CSVs.

No ROS node, simulator, remote connection or robot is started. The two data
figures use retained exports listed in report_validation.md; all others are
explicit explanatory schematics, not measured trajectories.
"""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Circle

HERE = Path(__file__).resolve().parent
EXP = Path('/home/mattb/Experiments/GESC-Gaussian/v3')
BLUE, GREEN, RED, GOLD, GRAY = '#285b8b', '#287b63', '#ab4247', '#ad761e', '#606b75'
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False,
                     'axes.spines.right': False, 'svg.fonttype': 'none',
                     'pdf.fonttype': 42, 'figure.facecolor': 'white'})


def save(fig, name):
    for suffix in ('pdf', 'svg'):
        fig.savefig(HERE / f'{name}.{suffix}', bbox_inches='tight', pad_inches=.12)
    plt.close(fig)


def box(ax, xy, size, text, color=BLUE, fontsize=12):
    x, y = xy; w, h = size
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.01',
                 facecolor=color+'12', edgecolor=color, linewidth=1.3))
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', color='#172d40', fontsize=fontsize)


def arrow(ax, a, b, label='', color=GRAY, dashed=False, offset=(0, .02)):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=12,
                 linewidth=1.3, color=color, linestyle='--' if dashed else '-'))
    if label:
        ax.text((a[0]+b[0])/2+offset[0], (a[1]+b[1])/2+offset[1], label,
                fontsize=11, ha='center', va='bottom', color=color,
                bbox=dict(facecolor='white', edgecolor='none', pad=1))


def architecture():
    fig, ax = plt.subplots(figsize=(10, 5.5)); ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    box(ax, (.02,.71), (.23,.18), 'Gazebo model\nbase odometry\nrotating-arm joint', GREEN, fontsize=11)
    box(ax, (.36,.73), (.26,.14), 'Modeled raw cost\nat observed sensor pose', GREEN, fontsize=11)
    box(ax, (.36,.42), (.26,.16), 'Observation adapter\npose, phase, raw cost\nidentity and original ages', fontsize=11)
    box(ax, (.72,.42), (.26,.16), 'V3 controller\nlocal state and registry\nbase command owner', RED, fontsize=11)
    box(ax, (.72,.74), (.26,.13), 'Private numerical worker\ncoherence or fill proposal', GOLD, fontsize=11)
    box(ax, (.72,.10), (.26,.14), 'Differential-drive base\n/cmd_vel subscriber', GREEN, fontsize=11)
    box(ax, (.02,.10), (.26,.16), 'Optional bag and plot\nobserve available streams', GRAY, fontsize=11)
    arrow(ax, (.25,.80), (.36,.80), 'sensor pose')
    arrow(ax, (.49,.73), (.49,.58), 'scalar cost', offset=(-.09,-.05))
    arrow(ax, (.25,.71), (.36,.53), 'observed support', offset=(-.08,-.02))
    ax.plot([.25,.30,.68], [.75,.66,.66], color=GRAY, lw=1.3)
    arrow(ax, (.68,.66), (.75,.58))
    ax.text(.43,.67,'current /odom',fontsize=11,ha='center',color=GRAY,
            bbox=dict(facecolor='white',edgecolor='none',pad=1))
    arrow(ax, (.62,.50), (.72,.50), 'observation', offset=(0,.10))
    ax.add_patch(FancyArrowPatch((.85,.58),(.85,.74),arrowstyle='<->',
                 mutation_scale=12,linewidth=1.3,color=GRAY))
    ax.text(.91,.63,'one job\none result',fontsize=10,color=GRAY)
    arrow(ax, (.85,.42), (.85,.24), '/cmd_vel', offset=(.08,0))
    arrow(ax, (.36,.44), (.28,.24), 'telemetry', dashed=True, offset=(-.02,0))
    arrow(ax, (.72,.46), (.28,.18), 'observed commands and events', dashed=True, offset=(0,-.03))
    ax.text(.5,.97,'Active V3 Gazebo information and authority flow',ha='center',weight='bold',fontsize=14)
    ax.text(.50,.02,'Hardware replaces the modeled device adapters; the shared algorithm remains in ros_esc.',ha='center',fontsize=10)
    save(fig, 'architecture')


def sensor_geometry():
    fig = plt.figure(figsize=(7,6))
    ax = fig.add_axes((.16,.13,.70,.64))
    ax.set_aspect('equal'); ax.set(xlim=(-.20,.27),ylim=(-.22,.21))
    yaw=np.deg2rad(25);phase=np.deg2rad(65);d=.18
    base=np.array([0.,0.]);sensor=d*np.array([np.cos(yaw+phase),np.sin(yaw+phase)])
    body=.20*np.array([np.cos(yaw),np.sin(yaw)])
    ax.add_patch(Circle(base,d,fill=False,ls='--',color=GRAY,lw=1))
    ax.annotate('',body,base,arrowprops=dict(arrowstyle='->',color=BLUE,lw=2))
    ax.text(body[0]+.007,body[1], 'body forward',color=BLUE)
    ax.plot([0,sensor[0]],[0,sensor[1]],color=GREEN,lw=3)
    ax.scatter(*base,s=100,color=BLUE,zorder=4); ax.scatter(*sensor,s=85,color=GREEN,zorder=4)
    ax.text(-.025,-.035,r'base $x_b$',ha='center');ax.text(.015,.187,r'sensor $x_s$',color=GREEN)
    ax.text(.009,.08,r'$d=0.18\ \mathrm{m}$',color=GREEN)
    ax.add_patch(Arc((0,0),.16,.16,theta1=0,theta2=25,color=BLUE,lw=1.6))
    ax.add_patch(Arc((0,0),.23,.23,theta1=25,theta2=90,color=GOLD,lw=1.6))
    ax.text(.082,.018,r'$\psi$',color=BLUE);ax.text(.07,.10,r'$\phi$',color=GOLD)
    ax.axhline(0,color=GRAY,lw=.7);ax.axvline(0,color=GRAY,lw=.7)
    ax.set_xlabel('world x coordinate (m)');ax.set_ylabel('world y coordinate (m)')
    fig.text(.5,.97,'Measured arm phase and base yaw locate the sensor',ha='center',weight='bold',fontsize=13)
    fig.text(.5,.89,r'$x_s=x_b+d[\cos(\psi+\phi),\ \sin(\psi+\phi)]$',ha='center',fontsize=14)
    fig.text(.5,.83,'Illustrative pose and angle; no source location is used.',ha='center',fontsize=11,color=GRAY)
    save(fig, 'sensor_geometry')


def objective_shapes():
    x=np.linspace(-2,3,800);raw=-.5*np.exp(-x*x/(2*.3**2))-1.3*np.exp(-(x-2.2)**2/(2*.45**2))
    fill=.8*np.exp(-x*x/(2*.65**2));affine=-.45*x
    fig, axs=plt.subplots(1,2,figsize=(10,4.6),sharex=True)
    axs[0].plot(x,raw,color=BLUE,label='raw source cost');axs[0].plot(x,fill,color=GREEN,label='positive Gaussian')
    axs[0].plot(x,raw+fill,color=RED,lw=2,label='SEARCH: raw + Gaussian')
    axs[1].plot(x,fill,color=GREEN,label='Gaussian');axs[1].plot(x,affine,color=GOLD,label='negative affine slope')
    axs[1].plot(x,fill+affine,color=RED,lw=2,label='ESCAPE: Gaussian + affine')
    for ax in axs:
        ax.axhline(0,color=GRAY,lw=.6);ax.axvline(0,color=GRAY,lw=.6,ls=':');ax.set_xlabel('schematic position')
        ax.set_ylabel('schematic signed cost');ax.legend(fontsize=12,loc='lower left');ax.grid(alpha=.15)
    axs[0].set_title('After a committed fill');axs[1].set_title('Raw attraction is disabled during escape')
    fig.suptitle('Cost shaping changes the function being minimized',weight='bold',fontsize=14,y=1.03)
    fig.text(.5,-.01,'Teaching curves only: not the actual photoresistor model, fitted basin or retained run.',ha='center',fontsize=10,color=GRAY)
    fig.tight_layout();save(fig,'objective_shapes')


def state_authority():
    fig,axs=plt.subplots(2,1,figsize=(10,6),gridspec_kw={'height_ratios':[1,1.4]})
    for ax in axs:ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    ax=axs[0];ax.text(0,1,'Command availability',weight='bold',fontsize=13)
    box(ax,(.02,.30),(.25,.35),'WAITING_INPUT\nzero commands',GRAY);box(ax,(.40,.30),(.22,.35),'ACTIVE\nfresh control',GREEN)
    box(ax,(.74,.30),(.24,.35),'STOPPED or FAULTED\nterminal zero',RED)
    arrow(ax,(.27,.57),(.40,.57),'fresh inputs');arrow(ax,(.40,.36),(.27,.36),'essential expiry',offset=(0,-.03))
    arrow(ax,(.62,.48),(.74,.48),'stop / fault')
    ax=axs[1];ax.text(0,1,'Local research activity while control is available',weight='bold',fontsize=13)
    for x,text,c in [(.02,'SEARCH\nGESC + confinement',BLUE),(.29,'VERIFY\nmoving raw evidence',GREEN),
                     (.56,'DESIGN\nworker proposal',GOLD),(.81,'ESCAPE\nshaped objective',RED)]:
        box(ax,(x,.49),(.17,.28),text,c)
    arrow(ax,(.19,.63),(.29,.63),'nominate');arrow(ax,(.46,.63),(.56,.63),'qualify');arrow(ax,(.73,.63),(.81,.63),'commit')
    arrow(ax,(.895,.49),(.895,.17));arrow(ax,(.895,.17),(.10,.17),'measured exit returns to SEARCH',offset=(0,.02));arrow(ax,(.10,.17),(.10,.49))
    ax.text(.5,.32,'Candidate or fit failure cancels research; fresh basic steering can continue.',ha='center',fontsize=10,color=GRAY)
    fig.tight_layout();save(fig,'state_authority')


def read_xy(path):
    with path.open() as f:
        rows=list(csv.DictReader(f))
    return np.array([[float(r[k]) for k in ('source_time_s','x','y')] for r in rows])


def gazebo_route():
    p=EXP/'affine_2_20260929T013558Z';data=read_xy(p/'analysis/csv/%2Fodom.csv');meta=json.loads((p/'outcome_geometry.json').read_text())
    fig,ax=plt.subplots(figsize=(8.5,6));t,x,y=data.T
    for a,b,label,col in [(0,144.7,'initial SEARCH',BLUE),(144.7,150.2,'VERIFY and DESIGN',GOLD),
                         (150.2,173.,'ESCAPE without direct assistance',RED),(173.,400.,'restored source seeking',GREEN)]:
        m=(t>=a)&(t<=b);ax.plot(x[m],y[m],color=col,label=label,lw=1.4)
    local=np.array([.5740251485476348,1.38581929876693]);glob=np.array([3.5,3.5]);f=meta['fill'];mu=(f['center_x'],f['center_y'])
    ax.scatter(*local,color=GOLD,s=100,marker='*',zorder=5);ax.annotate('400 lm source',local,xytext=(-1.05,2.2),arrowprops=dict(arrowstyle='-',color=GRAY),fontsize=10)
    ax.scatter(*glob,color=GREEN,s=150,marker='*',zorder=5);ax.text(3.12,3.70,'1600 lm source',fontsize=10,color=GREEN)
    ax.add_patch(Circle(mu,f['exit_radius'],fill=False,color=RED,ls='--',lw=1.2));ax.scatter(*mu,s=25,color=RED)
    ax.scatter(x[0],y[0],color=BLUE,s=45);ax.text(-.15,-.21,'start',color=BLUE)
    ax.scatter(x[-1],y[-1],color=GREEN,s=30);ax.annotate('final recorded pose', (x[-1],y[-1]),xytext=(2.25,4.15),arrowprops=dict(arrowstyle='-',color=GRAY),fontsize=10)
    ax.set_aspect('equal');ax.set(xlabel='observed odom x (m)',ylabel='observed odom y (m)',xlim=(-1.25,4.0),ylim=(-.35,4.55))
    ax.grid(alpha=.18);ax.legend(fontsize=9,loc='lower right',framealpha=.95)
    ax.set_title('Retained affine 2.0 selected Gazebo trial',loc='left',weight='bold',pad=12)
    fig.text(.5,.01,'Dashed circle: configured fill exit radius. Source positions are evaluator-only model data.',ha='center',fontsize=9,color=GRAY)
    fig.tight_layout(rect=(0,.035,1,1));save(fig,'gazebo_route')


def physical_route():
    path=EXP/'physical_runs/20260930T211613_989126Z-3555/analysis/csv/%2Fodom.csv';t,x,y=read_xy(path).T;t=t-t[0]
    fig,ax=plt.subplots(figsize=(7.5,5.5));pts=ax.scatter(x[::4],y[::4],c=t[::4],s=3,cmap='viridis',rasterized=False)
    ax.scatter(x[0],y[0],color=RED,marker='o',s=60,label='first recorded pose');ax.scatter(x[-1],y[-1],color=BLUE,marker='s',s=40,label='last recorded pose')
    ax.set_aspect('equal');ax.set(xlabel='OpenCR odom x (m)',ylabel='OpenCR odom y (m)');ax.grid(alpha=.18);ax.legend(fontsize=9,loc='upper left')
    cb=fig.colorbar(pts,ax=ax,pad=.04);cb.set_label('seconds from first recorded odometry')
    ax.set_title('Latest reviewed physical floor run stayed in SEARCH',loc='left',weight='bold',pad=12)
    fig.text(.5,.01,'No Vicon or lamp coordinates: the plot is odometry geometry, not lamp-centered orbit radius.',ha='center',fontsize=9,color=GRAY)
    fig.tight_layout(rect=(0,.035,1,1));save(fig,'physical_route')


def timing_contract():
    fig,ax=plt.subplots(figsize=(10,3.8));ax.set(xlim=(-.025,.72),ylim=(0,1));ax.axis('off')
    ax.plot([0,.65],[.45,.45],color=GRAY,lw=2)
    marks=[(0,'original\nsource time',BLUE),(.06,'first host\nreceipt',GREEN),(.30,'worker result\narrives',GOLD),(.50,'source-age\nexpiry',RED)]
    for i,(x,label,c) in enumerate(marks):
        label_y=.70 if i==1 else .55
        ax.plot([x,x],[.40,label_y-.03],color=c,lw=2)
        ax.text(x,label_y,label,ha='center',va='bottom',color=c,fontsize=11)
    arrow(ax,(0,.24),(.50,.24),'original source age keeps increasing',BLUE,offset=(0,.03))
    arrow(ax,(.06,.12),(.56,.12),'local elapsed receipt age also keeps increasing',GREEN,offset=(0,.02))
    ax.text(.32,.92,'Computation and queueing never make an old sample new',ha='center',weight='bold',fontsize=14)
    ax.text(.64,.38,'time (s)',ha='right',color=GRAY)
    ax.text(.32,.01,'Illustrative timing. Both age checks must pass; the result does not get a fresh timestamp.',ha='center',fontsize=10)
    save(fig,'timing_contract')


if __name__ == '__main__':
    for fn in (architecture,sensor_geometry,objective_shapes,state_authority,gazebo_route,physical_route,timing_contract):fn()
    print('Generated seven SVG/PDF figure pairs without ROS or hardware.')
