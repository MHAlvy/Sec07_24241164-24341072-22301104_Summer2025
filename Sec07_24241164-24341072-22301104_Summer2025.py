from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time
import os
game_state='MENU'
spaceship_pos=[0,0,-400]
spaceship_velocity=[0,0,0]
spaceship_angle=0.0
SPACESHIP_SIZE=25
ACCELERATION=1.5
DECELERATION=0.95
spaceship_models=[
    {'name':'Orbiter','draw_func':'draw_spaceship_model_orbiter','color':(0.9,0.9,1.0)}
]
selected_ship_index=0
health=100
max_health=100
lives=3
obstacles=[]
OBSTACLE_SPAWN_RATE=0.9
last_spawn_time=0
level=1
level_score_threshold=750
score=0
high_score=0
game_speed=1.0
lasers=[]
shatter_effects=[]
power_ups=[]
power_up_types={
    'shield':{'color':(0.2,0.5,1.0),'duration':10},
    'speed_boost':{'color':(1.0,1.0,0.0),'duration':8},
    'slow_mo':{'color':(0.0,1.0,1.0),'duration':7}
}
active_power_ups={}
last_power_up_spawn_time=0
is_invincible=False
spaceship_trail=[]
TRAIL_LENGTH=70
camera_mode='TPS'
camera_follow_angle=0.0
camera_follow_height=400.0
last_frame_time=0
show_hints=True
hint_timer=0
stars=[]

def load_high_score():
    global high_score
    if os.path.exists("highscore.txt"):
        with open("highscore.txt","r") as f:
            try:
                high_score=int(f.read())
            except ValueError:
                high_score=0
    else:
        high_score=0

def save_high_score():
    with open("highscore.txt","w") as f:
        f.write(str(int(high_score)))

def reset_game():
    global spaceship_pos,spaceship_velocity,spaceship_angle,obstacles,score,game_speed,last_spawn_time,last_frame_time,health,lives,level,game_state,lasers,shatter_effects,hint_timer,power_ups,active_power_ups,is_invincible,spaceship_trail,last_power_up_spawn_time,stars,camera_follow_angle,camera_follow_height
    spaceship_pos=[0,0,-400]
    spaceship_velocity=[0,0,0]
    spaceship_angle=0.0
    obstacles=[]
    lasers=[]
    shatter_effects=[]
    power_ups=[]
    active_power_ups={}
    spaceship_trail=[]
    is_invincible=False
    score=0
    health=max_health
    lives=3
    level=1
    game_speed=1.0
    current_time=time.time()
    last_spawn_time=current_time
    last_power_up_spawn_time=current_time
    last_frame_time=current_time
    hint_timer=current_time
    game_state='PLAYING'
    camera_follow_angle=0.0
    camera_follow_height=400.0
    stars=[]
    for i in range(9):
        stars.append({
            'pos':[random.uniform(-2000,2000),random.uniform(-1500,1500),random.uniform(1000,3000)],
            'phase':random.uniform(0,2*math.pi)
        })
    for i in range(10):
        spawn_obstacle()

def draw_text(x,y,text,font=GLUT_BITMAP_HELVETICA_18,center=False):
    if center:
        text_width=sum(glutBitmapWidth(font,ord(ch)) for ch in text)
        x-=text_width/2
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,1000,0,800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x,y)
    for ch in text:
        glutBitmapCharacter(font,ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_spaceship_model_orbiter():
    glPushMatrix()
    glRotatef(90,1,0,0)
    glColor3f(*spaceship_models[0]['color'])
    glutSolidSphere(SPACESHIP_SIZE,30,30)
    glColor3f(0.6,0.6,0.7)
    glPushMatrix()
    glRotatef(90,1,0,0)
    glutWireTorus(SPACESHIP_SIZE*0.03,SPACESHIP_SIZE*1.01,10,30)
    glPopMatrix()
    glPushMatrix()
    glRotatef(90,0,1,0)
    glutWireTorus(SPACESHIP_SIZE*0.03,SPACESHIP_SIZE*1.01,10,30)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0,0,SPACESHIP_SIZE*0.5)
    glRotatef(20,1,0,0)
    glColor3f(1.0,0.7,0.2)
    glutSolidSphere(SPACESHIP_SIZE*0.7,20,20)
    glColor3f(1.0,1.0,0.8)
    glTranslatef(SPACESHIP_SIZE*0.2,SPACESHIP_SIZE*0.3,SPACESHIP_SIZE*0.3)
    glutSolidSphere(SPACESHIP_SIZE*0.2,10,10)
    glPopMatrix()
    glColor3f(1.0,0.6,0.2)
    glPushMatrix()
    glTranslatef(SPACESHIP_SIZE*0.9,SPACESHIP_SIZE*0.2,0)
    glRotatef(45,0,0,1)
    glScalef(0.5,1.8,0.2)
    glutSolidSphere(SPACESHIP_SIZE*0.6,10,10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-SPACESHIP_SIZE*0.9,SPACESHIP_SIZE*0.2,0)
    glRotatef(-45,0,0,1)
    glScalef(0.5,1.8,0.2)
    glutSolidSphere(SPACESHIP_SIZE*0.6,10,10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0,SPACESHIP_SIZE*1.2,0)
    glRotatef(-90,1,0,0)
    glScalef(1.5,1.0,0.2)
    glutSolidCone(SPACESHIP_SIZE*0.4,SPACESHIP_SIZE*0.8,10,5)
    glPopMatrix()
    glColor3f(1.0,0.2,0.1)
    glPushMatrix()
    glTranslatef(0,-SPACESHIP_SIZE*0.8,0)
    quad=gluNewQuadric()
    gluCylinder(quad,SPACESHIP_SIZE*0.4,SPACESHIP_SIZE*0.7,SPACESHIP_SIZE*0.5,20,5)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0,-SPACESHIP_SIZE*1.2,0)
    glBegin(GL_TRIANGLE_STRIP)
    fire_length=SPACESHIP_SIZE*1.2
    for i in range(10):
        progress=i/9.0
        width=(1.0-progress)*SPACESHIP_SIZE*0.4+math.sin(time.time()*30+i)*2
        z_pos=progress*fire_length
        alpha=(1.0-progress)
        if progress<0.5:
            glColor4f(0.8,0.5,1.0,alpha)
        else:
            glColor4f(0.4,0.8,1.0,alpha*0.5)
        glVertex3f(width,z_pos,0)
        glVertex3f(-width,z_pos,0)
    glEnd()
    glPopMatrix()
    glPopMatrix()

def draw_spaceship():
    glPushMatrix()
    glTranslatef(spaceship_pos[0],spaceship_pos[1],spaceship_pos[2])
    glRotatef(spaceship_angle,0,1,0)
    if 'shield' in active_power_ups or is_invincible:
        glColor4f(0.5,0.8,1.0,0.3)
        glutSolidSphere(SPACESHIP_SIZE*1.8,20,20)
    draw_spaceship_model_orbiter()
    glPopMatrix()

def draw_obstacle_meteor(size,seed):
    glPushMatrix()
    random.seed(seed)
    for _ in range(7):
        offsetX=random.uniform(-0.3,0.3)*size*20
        offsetY=random.uniform(-0.3,0.3)*size*20
        offsetZ=random.uniform(-0.3,0.3)*size*20
        sub_size=random.uniform(0.4,0.8)*size*20
        grey_val=random.uniform(0.6,0.9)
        glPushMatrix()
        glTranslatef(offsetX,offsetY,offsetZ)
        glColor3f(grey_val,grey_val,grey_val)
        glutSolidSphere(sub_size,10,10)
        glPopMatrix()
    glBegin(GL_TRIANGLE_STRIP)
    tail_length=size*150
    for i in range(20):
        progress=i/19.0
        width=(1.0-progress)*size*25+math.sin(time.time()*20+i)*5
        z_pos=progress*tail_length
        alpha=(1.0-progress)*0.8
        if progress<0.3:
            glColor4f(1.0,1.0,0.2,alpha)
        elif progress<0.7:
            glColor4f(1.0,0.5,0.0,alpha)
        else:
            glColor4f(1.0,0.2,0.0,alpha*0.5)
        glVertex3f(width,0,z_pos)
        glVertex3f(-width,0,z_pos)
    glEnd()
    glPopMatrix()

def draw_obstacles():
    for obstacle in obstacles:
        glPushMatrix()
        glTranslatef(obstacle['pos'][0],obstacle['pos'][1],obstacle['pos'][2])
        draw_obstacle_meteor(obstacle['size'],obstacle['seed'])
        glPopMatrix()

def draw_lasers_and_effects():
    glColor3f(1,0.2,0.2)
    glLineWidth(3)
    glBegin(GL_LINES)
    for laser in lasers:
        glVertex3f(laser['pos'][0],laser['pos'][1],laser['pos'][2])
        glVertex3f(laser['pos'][0]+30*math.sin(math.radians(laser['angle'])),
                   laser['pos'][1],
                   laser['pos'][2]+30*math.cos(math.radians(laser['angle'])))
    glEnd()
    glLineWidth(1)
    glColor3f(1,0.8,0)
    glBegin(GL_LINES)
    for effect in shatter_effects:
        for line in effect['lines']:
            start_point=[effect['pos'][i]+line['dir'][i]*effect['life'] for i in range(3)]
            end_point=[effect['pos'][i]+line['dir'][i]*(effect['life']+20) for i in range(3)]
            glVertex3f(*start_point)
            glVertex3f(*end_point)
    glEnd()

def draw_power_ups():
    for pu in power_ups:
        glPushMatrix()
        glTranslatef(*pu['pos'])
        glRotatef(time.time()*70,0,1,1)
        glColor3f(*power_up_types[pu['type']]['color'])
        glScalef(15,15,15)
        if pu['type']=='shield':
            glutSolidOctahedron()
        elif pu['type']=='speed_boost':
            glutSolidTetrahedron()
        elif pu['type']=='slow_mo':
            glutSolidTorus(0.3,0.8,10,10)
        glPopMatrix()

def draw_spaceship_trail():
    if not spaceship_trail:
        return
    glLineWidth(4)
    glBegin(GL_LINE_STRIP)
    for i,point in enumerate(spaceship_trail):
        alpha=i/len(spaceship_trail)
        glColor4f(1.0,0.7,0.2,alpha*0.7)
        glVertex3f(*point)
    glEnd()
    glLineWidth(1)

def draw_level_background():
    if level==1:
        glPointSize(3)
        glBegin(GL_POINTS)
        for star in stars:
            brightness=0.6+0.4*math.sin(time.time()*2+star['phase'])
            glColor3f(brightness,brightness,brightness)
            glVertex3f(*star['pos'])
        glEnd()
    elif level==2:
        glBegin(GL_QUADS)
        for _ in range(25):
            glColor4f(random.uniform(0.5,1),0.2,random.uniform(0.5,1),0.1)
            x,y,z=random.uniform(-1000,1000),random.uniform(-500,500),random.uniform(0,1500)
            size=random.uniform(150,350)
            glVertex3f(x-size,y-size,z)
            glVertex3f(x+size,y-size,z)
            glVertex3f(x+size,y+size,z)
            glVertex3f(x-size,y+size,z)
        glEnd()
    elif level>=3:
        glColor3f(0.3,0.3,0.8)
        for z in range(0,2000,100):
            glPushMatrix()
            glTranslatef(0,0,z)
            glutWireTorus(5,500,4,20)
            glPopMatrix()

def draw_ui():
    draw_text(10,770,f"Score: {int(score)}")
    draw_text(10,740,f"High Score: {int(high_score)}")
    draw_text(800,770,f"Level: {level}")
    draw_text(800,740,f"Lives: {lives}")
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,1000,0,800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    y_pos=700
    for effect,timer in active_power_ups.items():
        draw_text(10,y_pos,f"{effect.upper()}: {int(timer)}s")
        y_pos-=30
    if is_invincible:
        draw_text(10,y_pos,"INVINCIBLE (CHEAT)")
    if show_hints and time.time()-hint_timer<10:
        draw_text(500,100,"Use W/S to move, A/D to turn",GLUT_BITMAP_HELVETICA_18,center=True)
        draw_text(500,70,"Arrow keys to control camera",GLUT_BITMAP_HELVETICA_18,center=True)
    elif show_hints and level>1 and time.time()-hint_timer<15:
        draw_text(500,100,f"Zone {level} Reached!",GLUT_BITMAP_TIMES_ROMAN_24,center=True)

def spawn_obstacle():
    GRID_LENGTH=700
    size=random.uniform(0.6,1.1)
    pos=[random.uniform(-GRID_LENGTH,GRID_LENGTH),0,random.uniform(GRID_LENGTH,GRID_LENGTH*2)]
    new_obstacle={
        'pos':pos,'type':'meteor','size':size,
        'velocity':[random.uniform(-50,50),0,-random.uniform(150,250)*game_speed],
        'seed':random.randint(0,10000)
    }
    obstacles.append(new_obstacle)

def spawn_power_up():
    GRID_LENGTH=600
    ptype=random.choice(list(power_up_types.keys()))
    pos=[random.uniform(-GRID_LENGTH/2,GRID_LENGTH/2),0,random.uniform(GRID_LENGTH,GRID_LENGTH*2)]
    new_power_up={
        'pos':pos,'type':ptype,'size':20,
        'velocity':[0,0,-180*game_speed]
    }
    power_ups.append(new_power_up)

def update_game_state(dt):
    global last_spawn_time,score,game_speed,level,hint_timer,last_power_up_spawn_time,active_power_ups
    effective_game_speed=game_speed*0.5 if 'slow_mo' in active_power_ups else game_speed
    GRID_LENGTH=600
    spaceship_pos[0]=max(-GRID_LENGTH,min(GRID_LENGTH,spaceship_pos[0]))
    spaceship_pos[2]=max(-GRID_LENGTH,min(GRID_LENGTH,spaceship_pos[2]))
    spaceship_trail.append(list(spaceship_pos))
    if len(spaceship_trail)>TRAIL_LENGTH:
        spaceship_trail.pop(0)
    for obj_list in [obstacles,power_ups]:
        for obj in obj_list:
            for i in range(3):obj['pos'][i]+=obj['velocity'][i]*dt*(effective_game_speed/game_speed)
    obstacles[:]=[obs for obs in obstacles if obs['pos'][2]>-GRID_LENGTH*2]
    power_ups[:]=[pu for pu in power_ups if pu['pos'][2]>-GRID_LENGTH*2]
    for laser in lasers:
        laser['pos'][0]+=20*math.sin(math.radians(laser['angle']))
        laser['pos'][2]+=20*math.cos(math.radians(laser['angle']))
    lasers[:]=[laser for laser in lasers if
                 -GRID_LENGTH<laser['pos'][0]<GRID_LENGTH and -GRID_LENGTH<laser['pos'][2]<GRID_LENGTH]
    for effect in shatter_effects:effect['life']+=dt*100
    shatter_effects[:]=[effect for effect in shatter_effects if effect['life']<effect['max_life']]
    active_power_ups={effect:timer-dt for effect,timer in active_power_ups.items() if timer-dt>0}
    current_time=time.time()
    if current_time-last_spawn_time>OBSTACLE_SPAWN_RATE:
        spawn_obstacle()
        last_spawn_time=current_time
    if current_time-last_power_up_spawn_time>10:
        spawn_power_up()
        last_power_up_spawn_time=current_time
    check_collisions()
    game_speed=1.0+(score/1000)
    if score>level*level_score_threshold:
        level+=1
        hint_timer=time.time()

def check_collisions():
    global health,lives,game_state,score,active_power_ups
    for obs in obstacles[:]:
        collision_distance=SPACESHIP_SIZE+(obs['size']*20)
        dist_vec=[spaceship_pos[i]-obs['pos'][i] for i in range(3)]
        distance=math.sqrt(sum(d**2 for d in dist_vec))
        if distance<collision_distance:
            if is_invincible or 'shield' in active_power_ups:
                create_shatter_effect(obs['pos'])
                obstacles.remove(obs)
                if not is_invincible:active_power_ups.pop('shield',None)
                continue
            create_shatter_effect(obs['pos'])
            obstacles.remove(obs)
            health-=34
            if health<=0:
                lives-=1
                if lives<=0:
                    game_state='GAME_OVER'
                    if score>high_score:save_high_score()
                else:
                    health=max_health
                    spaceship_pos[:]=[0,0,-400]
                    spaceship_velocity[:]=[0,0,0]
            break
    for pu in power_ups[:]:
        dist_vec=[spaceship_pos[i]-pu['pos'][i] for i in range(3)]
        distance=math.sqrt(sum(d**2 for d in dist_vec))
        if distance<(SPACESHIP_SIZE+pu['size']):
            active_power_ups[pu['type']]=power_up_types[pu['type']]['duration']
            power_ups.remove(pu)
            break
    for laser in lasers[:]:
        for obs in obstacles[:]:
            collision_distance=obs['size']*20
            dist_vec=[laser['pos'][i]-obs['pos'][i] for i in range(3)]
            distance=math.sqrt(sum(d**2 for d in dist_vec))
            if distance<collision_distance:
                create_shatter_effect(obs['pos'])
                obstacles.remove(obs)
                lasers.remove(laser)
                score+=50
                break

def create_shatter_effect(pos):
    effect={'pos':list(pos),'life':0,'max_life':50,'lines':[]}
    for _ in range(15):
        line={'dir':[random.uniform(-1,1) for _ in range(3)]}
        effect['lines'].append(line)
    shatter_effects.append(effect)

def keyboardListener(key,x,y):
    global game_state,is_invincible,spaceship_angle
    if key==b'q':
        glutLeaveMainLoop()
        return
    if game_state=='PLAYING':
        effective_move=20.0
        if key==b'w':
            spaceship_pos[0]+=effective_move
        if key==b's':
            spaceship_pos[0]-=effective_move
        if key==b'a':
            spaceship_angle+=5
        if key==b'd':
            spaceship_angle-=5
        GRID_LENGTH=600
        spaceship_pos[0]=max(-GRID_LENGTH,min(GRID_LENGTH,spaceship_pos[0]))
        if key==b'p':game_state='PAUSED'
        if key==b'i':is_invincible=not is_invincible
    elif game_state=='PAUSED':
        if key==b'p':game_state='PLAYING'
        if key==b'm':game_state='MENU'
    elif game_state=='GAME_OVER':
        if key==b'r':reset_game()
        if key==b'm':game_state='MENU'
    elif game_state=='MENU':
        if key==b'\r':reset_game()

def specialKeyListener(key,x,y):
    global camera_follow_angle,camera_follow_height
    if game_state=='PLAYING':
        if key==GLUT_KEY_RIGHT:
            camera_follow_angle-=5
        if key==GLUT_KEY_LEFT:
            camera_follow_angle+=5
        if key==GLUT_KEY_UP:
            camera_follow_height+=10
        if key==GLUT_KEY_DOWN:
            camera_follow_height-=10

def mouseListener(button,state,x,y):
    global camera_mode
    if game_state=='PLAYING' and button==GLUT_LEFT_BUTTON and state==GLUT_DOWN:
        laser_pos=list(spaceship_pos)
        lasers.append({'pos':laser_pos,'angle':spaceship_angle})
    if button==GLUT_RIGHT_BUTTON and state==GLUT_DOWN:
        camera_mode='FPS' if camera_mode=='TPS' else 'TPS'

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(75,1.25,1,4000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_mode=='TPS':
        cam_x=spaceship_pos[0]+camera_follow_height*math.sin(math.radians(camera_follow_angle))
        cam_z=spaceship_pos[2]+camera_follow_height*math.cos(math.radians(camera_follow_angle))
        gluLookAt(cam_x,camera_follow_height,cam_z,
                  spaceship_pos[0],spaceship_pos[1],spaceship_pos[2],
                  0,1,0)
    elif camera_mode=='FPS':
        eye_z=30
        look_at_x=spaceship_pos[0]+100*math.sin(math.radians(spaceship_angle))
        look_at_z=spaceship_pos[2]+100*math.cos(math.radians(spaceship_angle))
        gluLookAt(spaceship_pos[0],spaceship_pos[1]+eye_z,spaceship_pos[2],
                  look_at_x,spaceship_pos[1]+eye_z,look_at_z,
                  0,1,0)

def idle():
    global last_frame_time
    if game_state=='PLAYING':
        current_time=time.time()
        dt=current_time-last_frame_time
        last_frame_time=current_time
        if dt<0.1:update_game_state(dt)
    glutPostRedisplay()

def draw_menu_screen():
    draw_text(500,600,"3D SPACESHIP DODGE",GLUT_BITMAP_TIMES_ROMAN_24,center=True)
    draw_text(500,500,"Press ENTER to Start",GLUT_BITMAP_HELVETICA_18,center=True)
    draw_text(500,100,f"High Score: {int(high_score)}",GLUT_BITMAP_HELVETICA_18,center=True)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if game_state=='MENU':
        draw_menu_screen()
    elif game_state=='PLAYING' or game_state=='PAUSED':
        setupCamera()
        draw_level_background()
        draw_spaceship_trail()
        draw_spaceship()
        draw_obstacles()
        draw_power_ups()
        draw_lasers_and_effects()
        draw_ui()
        if game_state=='PAUSED':
            draw_text(500,400,"PAUSED",GLUT_BITMAP_TIMES_ROMAN_24,center=True)
            draw_text(500,370,"Press 'P' to Resume or 'M' for Menu",GLUT_BITMAP_HELVETICA_18,center=True)
    elif game_state=='GAME_OVER':
        draw_text(500,500,"GAME OVER",GLUT_BITMAP_TIMES_ROMAN_24,center=True)
        draw_text(500,450,f"Final Score: {int(score)}",GLUT_BITMAP_HELVETICA_18,center=True)
        if score>=high_score:
            draw_text(500,420,"New High Score!",GLUT_BITMAP_HELVETICA_18,center=True)
        draw_text(500,350,"Press 'R' to Restart or 'M' for Menu",GLUT_BITMAP_HELVETICA_18,center=True)
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(1000,800)
    glutInitWindowPosition(100,100)
    wind=glutCreateWindow(b"3D Spaceship Dodge - Final")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.0,0.0,0.0,1.0)
    load_high_score()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    print("Game Loaded. Main Menu Active.")
    glutMainLoop()

if __name__=="__main__":
    main()