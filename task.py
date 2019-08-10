import sys, time, os, random, struct, ctypes, subprocess, ctypes.wintypes
from random import randint
from base64 import a85decode
if subprocess._mswindows:
    import msvcrt
else:
    import tty,termios
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)
hStdOut = kernel32.GetStdHandle(-11)#STD_OUTPUT_HANDLE
hStdErr = kernel32.GetStdHandle(-12)#STD_ERROR_HANDLE
Player=chr(9608)
Wall=chr(9617)
Walk=" "

class sell(ctypes.Structure):
    _fields_ =[('char',ctypes.c_wchar),('status',ctypes.c_wchar_p)]

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [('dwSize', ctypes.c_int),('bVisible', ctypes.c_int)]
        
def maximize_console(lines=None):
    if subprocess._mswindows:
        SW_MAXIMIZE = 3
        hWnd = kernel32.GetConsoleWindow()
        user32.ShowWindow(hWnd, SW_MAXIMIZE)
    else:
        sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=9999,cols=9999))

def HideCursor():
    cursorInfo = CONSOLE_CURSOR_INFO()
    cursorInfo.dwSize = 1
    cursorInfo.bVisible = 0
    kernel32.SetConsoleCursorInfo(hStdOut,ctypes.byref(cursorInfo))
    
def print_at(r, c, s):
    if subprocess._mswindows:
        kernel32.SetConsoleCursorPosition(hStdOut, COORD(c, r))
        c = s.encode("cp866")
        kernel32.WriteConsoleA(hStdOut, ctypes.c_char_p(c), len(c), None, None)
    else:
        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (r+1,c+1,s))
        sys.stdout.flush()
        
def _getTerminalSize_windows():
    csbi = ctypes.create_string_buffer(22)
    res = kernel32.GetConsoleScreenBufferInfo(hStdErr, csbi)
    (bufx, bufy, curx, cury, wattr,
    left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
    sizex = right - left + 1
    sizey = bottom - top + 1
    return sizex, sizey
        
def cls(n):
    if subprocess._mswindows:
        os.system('cls')#clear screen
    else:
        os.system('clear')

def display(sells):
    s="\n".join(list(map(lambda x:"".join(list(map(lambda y:y.char,x))),sells)))
    print(s)#print maze
    n=len(s)
    return n

def checksells(position,sells,height,width):
    n=[]
    if position[0]>1:
        if sells[position[0]-2][position[1]].status=="NOTVISITED":
            n.append([position[0]-2,position[1]])
    if position[1]>1:
        if sells[position[0]][position[1]-2].status=="NOTVISITED":
            n.append([position[0],position[1]-2])
    if position[0]<height-2:
        if sells[position[0]+2][position[1]].status=="NOTVISITED":
            n.append([position[0]+2,position[1]])
    if position[1]<width-2:
        if sells[position[0]][position[1]+2].status=="NOTVISITED":
            n.append([position[0],position[1]+2])
    return n

def maze(width,height):
    cheat=""
    if subprocess._mswindows:
        kernel32.SetConsoleTextAttribute(hStdOut, 14)
    position=[1,1]#position in maze
    size=0#size of stack
    stack=[]
    sells=[[0 for i in range(width)] for i in range(height)]
    #maze filling
    for i in range(height):
        for j in range(width):
            if i%2!=0 and j%2!=0:
                sells[i][j]=sell()
                sells[i][j].char=Walk
                sells[i][j].status="NOTVISITED"
            else:
                sells[i][j]=sell()
                sells[i][j].char=Wall
                sells[i][j].status="WALL"
    sells[position[0]][position[1]].status="VISITED"
    bsells=len(checksells(position,sells,height,width))
    while size!=0 or bsells>0:
        if bsells>0:
            nextsell=checksells(position,sells,height,width)
            stack.append(position)
            size+=1
            position=nextsell[randint(0,len(nextsell)-1)]
            sells[(stack[size-1][0]+position[0])//2][(stack[size-1][1]+position[1])//2].char=Walk
            sells[(stack[size-1][0]+position[0])//2][(stack[size-1][1]+position[1])//2].status="VISITED"
            sells[stack[size-1][0]][stack[size-1][1]].char=Walk
            sells[stack[size-1][0]][stack[size-1][1]].status="VISITED"
        else:
            if size>0:
                sells[position[0]][position[1]].char=Walk
                sells[position[0]][position[1]].status="VISITED"
                position=stack[size-1]
                k=stack.pop()
                size-=1
        bsells=len(checksells(position,sells,height,width))
    statuskey=0
    x=1
    y=1
    n=0
    key="" #var for pressed key
    cls(n)
    n=display(sells)
    print_at(x, y, Player)
    while key!=b"q" and key!=b"\xa9" and key!="q" and (x!=height-2 or y!=width-2):
        if subprocess._mswindows:
            HideCursor()
        #whaiting key press
            while statuskey==0:
                statuskey=msvcrt.kbhit()#key check
            key=msvcrt.getch()#pressed key
        else:
            orig_setting=termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin)
            key=sys.stdin.read(1)[0]
        sells[x][y].char = Walk
        print_at(x, y, Walk)
        #pressed key check and update position if it is not wall or out of
        #range else do nothing
        if (key==b"w" or key==b"\xe6" or key=="w"):
            if not (x>=1 and sells[x-1][y].status != "WALL"):
                return 1
            cheat=""
            x-=1
            sells[x][y].char = Player
            print_at(x, y, Player)
            print_at(x+1, y, Walk)
        elif (key==b"s" or key==b"\xeb" or key=="s"):
            if not (x<=height-2 and sells[x+1][y].status != "WALL"):
                return 1
            cheat=""
            x+=1
            sells[x][y].char = Player
            print_at(x, y, Player)
            print_at(x-1, y, Walk)
        elif (key==b"d" or key==b"\xa2" or key=="d"):
            if not (y<=width-2 and sells[x][y+1].status != "WALL"):
                return 1
            cheat=""
            y+=1
            sells[x][y].char = Player
            print_at(x, y, Player)
            print_at(x, y-1, Walk)
        elif (key==b"a" or key==b"\xe4" or key=="a"):
            if not (y>=1 and sells[x][y-1].status != "WALL"):
                return 1
            cheat=""
            y-=1
            sells[x][y].char = Player
            print_at(x, y, Player)
            print_at(x, y+1, Walk)
        else:
            try:
                cheat+=key.decode();
            except:
                try:
                    cheat+=key
                except:pass
            if cheat=="mpeictf":
                break
            sells[x][y].char = Player
            print_at(x, y, Player)
        #update maze on screen
    print_at(x+2, 0, "")
    if subprocess._mswindows:
        kernel32.SetConsoleTextAttribute(hStdOut, 15)
    else:
        termios.tcsetattr(sys.stdin,termios.TCSADRAIN, orig_setting)
    if key==b"q" or key==b"\xa9" or key=="q":
        sys.exit()
    return 0
exec(a85decode(b'A7]?qASu$,DCIUR+<VdL+DGF1DEU-?3XQuP+<VdL+<Ve<G\\(A5@5p,TARfXhALM"874`@\\0h+;e;-,M*<B2["AL^,#5Yjj\'9eL6g2K(Zd6Y^Nn:h_=93b9I9,V;2;BN$Wp4$R4;5qX<k2*X/pBf8"[3%m!>-n&O[73ZDX/i=k+69oQ]D.kM=/Q4#G/nAO\'De*E-.4GTH+<VdLAScF!3XQuP+<VdL+<VeGEbTE5-mDE#@q?d)Ed8iX').decode())
print("Hello, that game labirint v1.0\nFor quit use 'q', for move in game use 'w','s','a','d'\nStayed final step! Go through the maze and you will get the answer to the riddle.\nYour goal is to get to the bottom right corner.\n\n\nPress someone key to start")
width=67 #width%2==1 TRUE 67 161
height=19 #height%2==1 TRUE 25 41
input()
r=maze(width,height)
while r:
    r=maze(width,height)
cls(0)
print("Did you think that was all? Haha, too easy...Your flag at the end of this mazes")
maximize_console()
input()
if subprocess._mswindows:
    size=_getTerminalSize_windows()
else:
    size=os.get_terminal_size()
width,height=(size[0]+(1-size[0]%2)-6,size[1]+(1-size[1]%2)-6)
n=0
for i in range(5):
    r=maze(width,height)
    n+=1
    while r:
        r=maze(width,height)
cls(0)
print(a85decode(b"6Z6jTEaa'2/0K4VFWbmBDBU-*Dfm17Cggs!BlbB").decode(),end="")
end(n)
input()
