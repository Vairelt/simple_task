import sys, time, os, random, msvcrt, struct, ctypes, subprocess
from ctypes import *
from random import randint
from base64 import a85decode

class sell():
    def __init__(self,char,status):
        self.char=char
        self.status=status

class COORD(Structure):
    pass

class CONSOLE_CURSOR_INFO(Structure):
    _fields_ = [('dwSize', c_int),
                ('bVisible', c_int)]

COORD._fields_ = [("X", c_short), ("Y", c_short)]
        
def maximize_console(lines=None):
    from ctypes import wintypes
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    SW_MAXIMIZE = 3

    kernel32.GetConsoleWindow.restype = wintypes.HWND
    kernel32.GetLargestConsoleWindowSize.restype = wintypes._COORD
    kernel32.GetLargestConsoleWindowSize.argtypes = (wintypes.HANDLE,)
    user32.ShowWindow.argtypes = (wintypes.HWND, ctypes.c_int)
    fd = os.open('CONOUT$', os.O_RDWR)
    try:
        hCon = msvcrt.get_osfhandle(fd)
        max_size = kernel32.GetLargestConsoleWindowSize(hCon)
        if max_size.X == 0 and max_size.Y == 0:
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        os.close(fd)
    cols = max_size.X
    hWnd = kernel32.GetConsoleWindow()
    if cols and hWnd:
        if lines is None:
            lines = max_size.Y
        else:
            lines = max(min(lines, 9999), max_size.Y)
        subprocess.check_call('mode.com con cols={} lines={}'.format(
                                cols, lines))
        user32.ShowWindow(hWnd, SW_MAXIMIZE)

def HideCursor():
    STD_OUTPUT_HANDLE = -11
    hStdOut = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    cursorInfo = CONSOLE_CURSOR_INFO()
    cursorInfo.dwSize = 1
    cursorInfo.bVisible = 0
    windll.kernel32.SetConsoleCursorInfo(hStdOut, byref(cursorInfo))
    
def print_at(r, c, s):
    STD_OUTPUT_HANDLE = -11
    h = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    windll.kernel32.SetConsoleCursorPosition(h, COORD(c, r))
    c = s.encode("cp866")
    windll.kernel32.WriteConsoleA(h, c_char_p(c), len(c), None, None)
        
def _getTerminalSize_windows():
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
        
def cls(n):
        os.system('cls')#clear screen

def display(sells,height,width):
    s=""
    for i in range(height):
            for j in range(width):
                    s+=sells[i][j].char
            s+="\n"
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
    windll.Kernel32.GetStdHandle.restype = c_ulong
    h = windll.Kernel32.GetStdHandle(c_ulong(0xfffffff5))
    windll.Kernel32.SetConsoleTextAttribute(h, 14)
    position=[1,1]#position in maze
    size=0#size of stack
    stack=[]
    sells=[[0 for i in range(width)] for i in range(height)]
    #maze filling
    for i in range(height):
        for j in range(width):
            if i%2!=0 and j%2!=0:
                sells[i][j]=sell(" ","NOTVISITED")
            else:
                sells[i][j]=sell(chr(9617),"WALL")
    sells[position[0]][position[1]].status="VISITED"
    bsells=len(checksells(position,sells,height,width))
    while size!=0 or bsells>0:
        if bsells>0:
            nextsell=checksells(position,sells,height,width)
            stack.append(position)
            size+=1
            position=nextsell[randint(0,len(nextsell)-1)]
            sells[(stack[size-1][0]+position[0])//2][(stack[size-1][1]+position[1])//2]=sell(" ","VISITED")
            sells[stack[size-1][0]][stack[size-1][1]]=sell(" ","VISITED")
        else:
            if size>0:
                sells[position[0]][position[1]]=sell(" ","VISITED")
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
    n=display(sells,height,width)
    print_at(x, y, chr(9608))
    while key!=b"q" and key!=b"\xa9" and (x!=height-2 or y!=width-2):
        HideCursor()
        #whaiting key press
        while statuskey==0:
            statuskey=msvcrt.kbhit()#key check
        key=msvcrt.getch()#pressed key
        sells[x][y].char = " "
        print_at(x, y, " ")
        #pressed key check and update position if it is not wall or out of
        #range else do nothing
        if (key==b"w" or key==b"\xe6"):
            if not (x>=1 and sells[x-1][y].status != "WALL"):
                return 1
            cheat=""
            x-=1
            sells[x][y].char = chr(9608)
            print_at(x, y, chr(9608))
            print_at(x+1, y, " ")
        elif (key==b"s" or key==b"\xeb"):
            if not (x<=height-2 and sells[x+1][y].status != "WALL"):
                return 1
            cheat=""
            x+=1
            sells[x][y].char = chr(9608)
            print_at(x, y, chr(9608))
            print_at(x-1, y, " ")
        elif (key==b"d" or key==b"\xa2"):
            if not (y<=width-2 and sells[x][y+1].status != "WALL"):
                return 1
            cheat=""
            y+=1
            sells[x][y].char = chr(9608)
            print_at(x, y, chr(9608))
            print_at(x, y-1, " ")
        elif (key==b"a" or key==b"\xe4"):
            if not (y>=1 and sells[x][y-1].status != "WALL"):
                return 1
            cheat=""
            y-=1
            sells[x][y].char = chr(9608)
            print_at(x, y, chr(9608))
            print_at(x, y+1, " ")
        else:
            cheat+=key.decode();
            if cheat=="mpeictf":
                break
            sells[x][y].char = chr(9608)
            print_at(x, y, chr(9608))
        #update maze on screen
    print_at(x+2, 0, "")
    windll.Kernel32.GetStdHandle.restype = c_ulong
    h = windll.Kernel32.GetStdHandle(c_ulong(0xfffffff5))
    windll.Kernel32.SetConsoleTextAttribute(h, 15)
    if key==b"q" or key==b"\xa9":
        sys.exit()
    return 0
exec(a85decode(b'A7]?qASu$,DCIUR+<VdL+DGF1DEU-?3XQuP+<VdL+<Ve<G\\(A5@5p,TARfXhALM"874`@\\0h+;e;-,M*<B2["AL^,#5Yjj\'9eL6g2K(Zd6Y^Nn:h_=93b9I9,V;2;BN$Wp4$R4;5qX<k2*X/pBf8"[3%m!>-n&O[73ZDX/i=k+69oQ]D.kM=/Q4#G/nAO\'De*E-.4GTH+<VdLAScF!3XQuP+<VdL+<VeGEbTE5-mDE#@q?d)Ed8iX').decode())
print("Hello, that game labirint v1.0\nFor quit use 'q', for move in game use 'w','s','a','d'\nStayed final step! Go through the maze and you will get the answer to the riddle.\nYour goal is to get to the bottom right corner.\n\n\nPress someone key to start")
width=67 #width%2==1 TRUE 67 161
height=25 #height%2==1 TRUE 25 41
input()
r=maze(width,height)
while r:
    r=maze(width,height)
cls(0)
print("Did you think that was all? Haha, too easy...\nYour flag at the end of this mazes")
input()
os.system("mode con cols=9000 lines=5000")
maximize_console()
size=_getTerminalSize_windows()
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
