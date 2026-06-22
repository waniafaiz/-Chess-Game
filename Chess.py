
import sys, os, copy, math, time, random, threading, urllib.request
import pygame

# ═══════════════════════════════════════════════════════════════════════════════
#  ASSETS
# ═══════════════════════════════════════════════════════════════════════════════

PIECE_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pieces")
PIECE_NAMES = ["wK","wQ","wR","wB","wN","wP","bK","bQ","bR","bB","bN","bP"]
SQ          = 76   # square px

def ensure_pieces():
    os.makedirs(PIECE_DIR, exist_ok=True)
    # Piece images will be used if available, otherwise unicode fallbacks will be displayed

# ═══════════════════════════════════════════════════════════════════════════════
#  COLOURS & THEME
# ═══════════════════════════════════════════════════════════════════════════════

C = dict(
    bg          = (18, 14, 10),
    board_light = (240, 217, 181),
    board_dark  = (181, 136,  99),
    border      = (90,  65,  35),
    border2     = (140, 100,  55),
    gold        = (212, 175,  80),
    gold_dim    = (150, 120,  55),
    cream       = (242, 232, 210),
    text        = (232, 222, 200),
    text_dim    = (140, 120,  90),
    text_dark   = ( 28,  22,  15),
    sel         = ( 90, 190,  70, 190),
    hint        = ( 60, 140,  50, 150),
    cap_ring    = (195,  50,  45, 200),
    last_mv     = (200, 210,  90, 120),
    check       = (215,  38,  38, 170),
    btn_bg      = ( 50,  38,  24),
    btn_hover   = ( 75,  58,  36),
    btn_active  = (100,  78,  48),
    btn_border  = (140, 100,  55),
    panel       = ( 26,  20,  13),
    panel2      = ( 36,  28,  18),
    green       = ( 72, 185,  85),
    red         = (205,  60,  55),
    blue        = ( 80, 140, 210),
    yellow      = (220, 190,  60),
    white       = (255, 255, 255),
    black       = (  0,   0,   0),
)

def col(k, a=None):
    v = C[k]
    if a is not None: return (*v[:3], a)
    return v

# ═══════════════════════════════════════════════════════════════════════════════
#  CHESS LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

PIECE_VAL = {"P":100,"N":320,"B":330,"R":500,"Q":900,"K":20000}

# Piece-square tables (white, from white's perspective row 0=rank8)
PST = {
"P": [[ 0,  0,  0,  0,  0,  0,  0,  0],
      [50, 50, 50, 50, 50, 50, 50, 50],
      [10, 10, 20, 30, 30, 20, 10, 10],
      [ 5,  5, 10, 25, 25, 10,  5,  5],
      [ 0,  0,  0, 20, 20,  0,  0,  0],
      [ 5, -5,-10,  0,  0,-10, -5,  5],
      [ 5, 10, 10,-20,-20, 10, 10,  5],
      [ 0,  0,  0,  0,  0,  0,  0,  0]],
"N": [[-50,-40,-30,-30,-30,-30,-40,-50],
      [-40,-20,  0,  0,  0,  0,-20,-40],
      [-30,  0, 10, 15, 15, 10,  0,-30],
      [-30,  5, 15, 20, 20, 15,  5,-30],
      [-30,  0, 15, 20, 20, 15,  0,-30],
      [-30,  5, 10, 15, 15, 10,  5,-30],
      [-40,-20,  0,  5,  5,  0,-20,-40],
      [-50,-40,-30,-30,-30,-30,-40,-50]],
"B": [[-20,-10,-10,-10,-10,-10,-10,-20],
      [-10,  0,  0,  0,  0,  0,  0,-10],
      [-10,  0,  5, 10, 10,  5,  0,-10],
      [-10,  5,  5, 10, 10,  5,  5,-10],
      [-10,  0, 10, 10, 10, 10,  0,-10],
      [-10, 10, 10, 10, 10, 10, 10,-10],
      [-10,  5,  0,  0,  0,  0,  5,-10],
      [-20,-10,-10,-10,-10,-10,-10,-20]],
"R": [[ 0,  0,  0,  0,  0,  0,  0,  0],
      [ 5, 10, 10, 10, 10, 10, 10,  5],
      [-5,  0,  0,  0,  0,  0,  0, -5],
      [-5,  0,  0,  0,  0,  0,  0, -5],
      [-5,  0,  0,  0,  0,  0,  0, -5],
      [-5,  0,  0,  0,  0,  0,  0, -5],
      [-5,  0,  0,  0,  0,  0,  0, -5],
      [ 0,  0,  0,  5,  5,  0,  0,  0]],
"Q": [[-20,-10,-10, -5, -5,-10,-10,-20],
      [-10,  0,  0,  0,  0,  0,  0,-10],
      [-10,  0,  5,  5,  5,  5,  0,-10],
      [ -5,  0,  5,  5,  5,  5,  0, -5],
      [  0,  0,  5,  5,  5,  5,  0, -5],
      [-10,  5,  5,  5,  5,  5,  0,-10],
      [-10,  0,  5,  0,  0,  0,  0,-10],
      [-20,-10,-10, -5, -5,-10,-10,-20]],
"K": [[-30,-40,-40,-50,-50,-40,-40,-30],
      [-30,-40,-40,-50,-50,-40,-40,-30],
      [-30,-40,-40,-50,-50,-40,-40,-30],
      [-30,-40,-40,-50,-50,-40,-40,-30],
      [-20,-30,-30,-40,-40,-30,-30,-20],
      [-10,-20,-20,-20,-20,-20,-20,-10],
      [ 20, 20,  0,  0,  0,  0, 20, 20],
      [ 20, 30, 10,  0,  0, 10, 30, 20]],
}

class Piece:
    __slots__ = ("color","row","col","sym","moved")
    def __init__(self, color, row, col, sym):
        self.color=color; self.row=row; self.col=col; self.sym=sym; self.moved=False
    def enemy(self,p): return p and p.color!=self.color
    def friend(self,p): return p and p.color==self.color
    def ib(self,r,c): return 0<=r<8 and 0<=c<8
    def slides(self,board,dirs):
        mv=[]
        for dr,dc in dirs:
            r,c=self.row+dr,self.col+dc
            while self.ib(r,c):
                t=board[r][c]
                if t is None: mv.append((r,c))
                elif self.enemy(t): mv.append((r,c)); break
                else: break
                r+=dr; c+=dc
        return mv
    def pseudo(self,board): return []
    def pst_score(self):
        table=PST.get(self.sym)
        if not table: return 0
        r=self.row if self.color=="black" else 7-self.row
        return table[r][self.col]
    def __repr__(self): return f"{self.color[0]}{self.sym}"

class Pawn(Piece):
    def __init__(self,c,r,col): super().__init__(c,r,col,"P")
    def pseudo(self,board):
        mv=[]; d=-1 if self.color=="white" else 1; sr=6 if self.color=="white" else 1
        r,c=self.row+d,self.col
        if self.ib(r,c) and not board[r][c]:
            mv.append((r,c))
            if self.row==sr and not board[self.row+2*d][c]: mv.append((self.row+2*d,c))
        for dc in(-1,1):
            r2,c2=self.row+d,self.col+dc
            if self.ib(r2,c2) and self.enemy(board[r2][c2]): mv.append((r2,c2))
        return mv
    def ep_moves(self,ep):
        if not ep: return []
        d=-1 if self.color=="white" else 1
        if ep[0]==self.row+d and abs(ep[1]-self.col)==1: return [ep]
        return []

class Rook(Piece):
    def __init__(self,c,r,col): super().__init__(c,r,col,"R")
    def pseudo(self,board): return self.slides(board,[(-1,0),(1,0),(0,-1),(0,1)])

class Knight(Piece):
    def __init__(self,c,r,col): super().__init__(c,r,col,"N")
    def pseudo(self,board):
        return [(self.row+dr,self.col+dc) for dr,dc in
                [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
                if self.ib(self.row+dr,self.col+dc) and not self.friend(board[self.row+dr][self.col+dc])]

class Bishop(Piece):
    def __init__(self,c,r,col): super().__init__(c,r,col,"B")
    def pseudo(self,board): return self.slides(board,[(-1,-1),(-1,1),(1,-1),(1,1)])

class Queen(Piece):
    def __init__(self,c,r,col): super().__init__(c,r,col,"Q")
    def pseudo(self,board): return self.slides(board,[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)])

class King(Piece):
    def __init__(self,c,r,col): super().__init__(c,r,col,"K")
    def pseudo(self,board):
        return [(self.row+dr,self.col+dc) for dr in(-1,0,1) for dc in(-1,0,1)
                if (dr or dc) and self.ib(self.row+dr,self.col+dc) and not self.friend(board[self.row+dr][self.col+dc])]
    def castles(self,board,attacked):
        mv=[]; row=self.row
        if self.moved or (row,4) in attacked: return mv
        rk=board[row][7]
        if isinstance(rk,Rook) and not rk.moved and not board[row][5] and not board[row][6] \
                and (row,5) not in attacked and (row,6) not in attacked: mv.append((row,6))
        rk=board[row][0]
        if isinstance(rk,Rook) and not rk.moved and not board[row][1] and not board[row][2] \
                and not board[row][3] and (row,3) not in attacked and (row,2) not in attacked: mv.append((row,2))
        return mv

BACK=[Rook,Knight,Bishop,Queen,King,Bishop,Knight,Rook]
PROMO_MAP={"Q":Queen,"R":Rook,"B":Bishop,"N":Knight}

def start_board():
    b=[[None]*8 for _ in range(8)]
    for c,Cls in enumerate(BACK):
        b[0][c]=Cls("black",0,c); b[7][c]=Cls("white",7,c)
    for c in range(8):
        b[1][c]=Pawn("black",1,c); b[6][c]=Pawn("white",6,c)
    return b

def attacked_by(board,color):
    sq=set()
    for row in board:
        for p in row:
            if not p or p.color!=color: continue
            if isinstance(p,Pawn):
                d=-1 if p.color=="white" else 1
                for dc in(-1,1):
                    if 0<=p.row+d<8 and 0<=p.col+dc<8: sq.add((p.row+d,p.col+dc))
            elif isinstance(p,King):
                for dr in(-1,0,1):
                    for dc in(-1,0,1):
                        if (dr or dc) and 0<=p.row+dr<8 and 0<=p.col+dc<8: sq.add((p.row+dr,p.col+dc))
            else: sq.update(p.pseudo(board))
    return sq

def find_king(board,color):
    for row in board:
        for p in row:
            if isinstance(p,King) and p.color==color: return p.row,p.col
    return None

def in_check(board,color):
    kp=find_king(board,color)
    if not kp: return False
    return kp in attacked_by(board,"black" if color=="white" else "white")

def do_move(board,fr,to,ep=None,promo="Q"):
    board=copy.deepcopy(board)
    frow,fcol=fr; trow,tcol=to
    p=board[frow][fcol]; new_ep=None
    if isinstance(p,Pawn) and ep==(trow,tcol): board[frow][tcol]=None
    if isinstance(p,Pawn) and abs(trow-frow)==2: new_ep=((frow+trow)//2,tcol)
    if isinstance(p,King) and abs(tcol-fcol)==2:
        if tcol==6:
            rk=board[trow][7]; board[trow][5]=rk; board[trow][7]=None
            if rk: rk.col=5; rk.moved=True
        else:
            rk=board[trow][0]; board[trow][3]=rk; board[trow][0]=None
            if rk: rk.col=3; rk.moved=True
    board[frow][fcol]=None; board[trow][tcol]=p
    p.row=trow; p.col=tcol; p.moved=True
    if isinstance(p,Pawn) and (trow==0 or trow==7):
        cls=PROMO_MAP.get(promo,Queen)
        board[trow][tcol]=cls(p.color,trow,tcol)
    return board,new_ep

def legal_moves(board,piece,ep=None):
    moves=piece.pseudo(board)
    if isinstance(piece,Pawn): moves+=piece.ep_moves(ep)
    if isinstance(piece,King):
        en="black" if piece.color=="white" else "white"
        moves+=piece.castles(board,attacked_by(board,en))
    legal=[]
    for t in moves:
        nb,_=do_move(board,(piece.row,piece.col),t,ep)
        if not in_check(nb,piece.color): legal.append(t)
    return legal

def all_legal_moves(board,color,ep=None):
    result=[]
    for row in board:
        for p in row:
            if p and p.color==color:
                for t in legal_moves(board,p,ep):
                    result.append(((p.row,p.col),t))
    return result

def game_status(board,turn,ep=None):
    chk=in_check(board,turn)
    moves=all_legal_moves(board,turn,ep)
    if not moves: return "checkmate" if chk else "stalemate"
    if chk: return "check"
    pieces=[p for row in board for p in row if p]
    syms=[type(p).__name__ for p in pieces]
    if len(pieces)==2: return "draw"
    if len(pieces)==3 and ("Bishop" in syms or "Knight" in syms): return "draw"
    return "ongoing"

# ── Evaluation ──────────────────────────────────────────────────────────────────

def evaluate(board):
    score=0
    for row in board:
        for p in row:
            if not p: continue
            v=PIECE_VAL.get(p.sym,0)+p.pst_score()
            score += v if p.color=="white" else -v
    return score

def minimax(board,depth,alpha,beta,maximizing,ep):
    st=game_status(board,"white" if maximizing else "black",ep)
    if st=="checkmate": return -50000 if maximizing else 50000
    if st in("stalemate","draw"): return 0
    if depth==0: return evaluate(board)
    color="white" if maximizing else "black"
    moves=all_legal_moves(board,color,ep)
    random.shuffle(moves)
    if maximizing:
        best=-999999
        for fr,to in moves:
            nb,nep=do_move(board,fr,to,ep)
            best=max(best,minimax(nb,depth-1,alpha,beta,False,nep))
            alpha=max(alpha,best)
            if beta<=alpha: break
        return best
    else:
        best=999999
        for fr,to in moves:
            nb,nep=do_move(board,fr,to,ep)
            best=min(best,minimax(nb,depth-1,alpha,beta,True,nep))
            beta=min(beta,best)
            if beta<=alpha: break
        return best

DEPTH_MAP={"Easy":1,"Medium":3,"Hard":4}

def ai_move(board,color,difficulty,ep):
    depth=DEPTH_MAP.get(difficulty,2)
    moves=all_legal_moves(board,color,ep)
    if not moves: return None,None
    maximizing=(color=="white")
    best_score=None; best_move=None
    random.shuffle(moves)
    for fr,to in moves:
        nb,nep=do_move(board,fr,to,ep)
        score=minimax(nb,depth-1,-999999,999999,not maximizing,nep)
        if best_score is None or (maximizing and score>best_score) or (not maximizing and score<best_score):
            best_score=score; best_move=(fr,to)
    return best_move

# ═══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_rounded_rect(surf, color, rect, radius=10, border=0, border_color=None):
    x,y,w,h=rect
    s=pygame.Surface((w,h),pygame.SRCALPHA)
    pygame.draw.rect(s,color,(0,0,w,h),border_radius=radius)
    surf.blit(s,(x,y))
    if border and border_color:
        pygame.draw.rect(surf,border_color,rect,border,border_radius=radius)

def draw_text(surf,text,font,color,cx,cy,anchor="center"):
    t=font.render(text,True,color)
    r=t.get_rect()
    if anchor=="center": r.center=(cx,cy)
    elif anchor=="left": r.midleft=(cx,cy)
    elif anchor=="right": r.midright=(cx,cy)
    surf.blit(t,r)
    return r

class Button:
    def __init__(self,rect,label,icon=None,style="default"):
        self.rect=pygame.Rect(rect)
        self.label=label; self.icon=icon; self.style=style
        self.hovered=False; self.pressed=False
    def update(self,pos):
        self.hovered=self.rect.collidepoint(pos)
    def handle(self,ev):
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and self.hovered:
            self.pressed=True; return True
        return False
    def draw(self,surf,font):
        if self.style=="ghost":
            bg=col("btn_hover") if self.hovered else (0,0,0,0)
            bc=col("gold") if self.hovered else col("gold_dim")
        elif self.style=="danger":
            bg=col("red") if self.hovered else (120,35,30)
            bc=(200,70,65)
        elif self.style=="success":
            bg=(50,140,60) if self.hovered else (35,100,45)
            bc=col("green")
        else:
            bg=col("btn_hover") if self.hovered else col("btn_bg")
            bc=col("btn_border")
        draw_rounded_rect(surf,bg,self.rect,8,2,bc)
        tc=col("gold") if self.hovered else col("cream")
        t=font.render(self.label,True,tc)
        
        if self.icon:
            ic=font.render(self.icon,True,col("gold"))
            # Calculate total width of icon + space + text
            total_width=ic.get_width()+16+t.get_width()
            start_x=self.rect.centerx-total_width//2
            # Draw icon
            surf.blit(ic,(start_x,self.rect.y+(self.rect.h-ic.get_height())//2))
            # Draw text next to icon
            surf.blit(t,(start_x+ic.get_width()+16,self.rect.y+(self.rect.h-t.get_height())//2))
        else:
            surf.blit(t,(self.rect.centerx-t.get_width()//2,self.rect.y+(self.rect.h-t.get_height())//2))

class ToggleGroup:
    """A row of exclusive option buttons."""
    def __init__(self,rect,options,default=0):
        self.options=options; self.sel=default
        x,y,w,h=rect
        bw=w//len(options)
        self.rects=[pygame.Rect(x+i*bw,y,bw,h) for i in range(len(options))]
    def handle(self,ev):
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            for i,r in enumerate(self.rects):
                if r.collidepoint(ev.pos): self.sel=i; return True
        return False
    def draw(self,surf,font,pos):
        for i,(r,opt) in enumerate(zip(self.rects,self.options)):
            active=(i==self.sel); hov=r.collidepoint(pos)
            bg=col("gold") if active else (col("btn_hover") if hov else col("btn_bg"))
            tc=col("text_dark") if active else (col("cream") if hov else col("text_dim"))
            draw_rounded_rect(surf,bg,r,6,2,col("btn_border"))
            draw_text(surf,opt,font,tc,r.centerx,r.centery)
    @property
    def value(self): return self.options[self.sel]

# ═══════════════════════════════════════════════════════════════════════════════
#  SCREENS
# ═══════════════════════════════════════════════════════════════════════════════

# Window layout
WIN_W = 1100
WIN_H = 780
BOARD_X = 200          # board left edge
BOARD_Y = 50
BORDER  = 32           # label margin
SIDEBAR_X = BOARD_X + BORDER + 8*SQ + BORDER + 10
SIDEBAR_W = WIN_W - SIDEBAR_X - 10

FILES="abcdefgh"; RANKS="87654321"

UNICODE_PIECES = {
    ("white","K"):"♔",("white","Q"):"♕",("white","R"):"♖",
    ("white","B"):"♗",("white","N"):"♘",("white","P"):"♙",
    ("black","K"):"♚",("black","Q"):"♛",("black","R"):"♜",
    ("black","B"):"♝",("black","N"):"♞",("black","P"):"♟",
}


class RoyalChess:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((WIN_W,WIN_H))
        pygame.display.set_caption("  Royal Chess ")
        self.clock=pygame.time.Clock()

        # Fonts
        self.f_title = pygame.font.SysFont("Georgia,serif",54,bold=True)
        self.f_h2    = pygame.font.SysFont("Georgia,serif",28,bold=True)
        self.f_h3    = pygame.font.SysFont("Georgia,serif",20,bold=True)
        self.f_body  = pygame.font.SysFont("Georgia,serif",15)
        self.f_small = pygame.font.SysFont("Georgia,serif",12)
        self.f_piece = pygame.font.SysFont("segoeuisymbol,symbola,dejavusans",SQ-8)
        self.f_icon  = pygame.font.SysFont("segoeuisymbol,symbola,dejavusans",20)

        ensure_pieces()
        self.imgs=self._load_imgs()

        # Global state
        self.scene="menu"
        self.scores={"white":0,"black":0,"draws":0}
        self.total_rounds=3
        self.rounds_played=0
        self.ai_color=None        # which color is AI
        self.difficulty="Medium"
        self.mode="pvp"           # pvp / pvc

        # Per-game state (set by new_game)
        self.board=None
        self.turn=None
        self.sel=None; self.hints=[]; self.ep=None
        self.last_move=None; self.status="ongoing"
        self.move_num=1
        self.captured={"white":[],"black":[]}
        self.promo_ctx=None
        self.move_history=[]
        self.w_time=0; self.b_time=0; self.t_start=0
        self.paused=False
        self.ai_thinking=False
        self.ai_result=None
        self.result_shown=False   # waiting for "Next Round" click

        # Menu UI
        self._build_menu_ui()
        self._build_pause_ui()
        self._anim=0.0

    # ── Asset loading ─────────────────────────────────────────────────────────

    def _load_imgs(self):
        imgs={}
        for n in PIECE_NAMES:
            p=os.path.join(PIECE_DIR,f"{n}.png")
            if os.path.exists(p):
                imgs[n]=pygame.image.load(p).convert_alpha()
        return imgs

    def _piece_img(self,piece,size=None):
        key=("w" if piece.color=="white" else "b")+piece.sym
        img=self.imgs.get(key)
        if img and size:
            return pygame.transform.smoothscale(img,(size,size))
        return img

    # ── Menu UI ───────────────────────────────────────────────────────────────

    def _build_menu_ui(self):
        cx=WIN_W//2
        self.tg_mode   =ToggleGroup((cx-200,250,400,42),["Player vs Player","Player vs CPU"],0)
        self.tg_diff   =ToggleGroup((cx-200,345,400,42),["Easy","Medium","Hard"],1)
        self.tg_rounds =ToggleGroup((cx-200,440,400,42),["1 Round","3 Rounds","5 Rounds"],1)
        self.btn_start =Button((cx-130,525,260,55)," Start Game","","success")

    def _build_pause_ui(self):
        cx=WIN_W//2; cy=WIN_H//2
        self.btn_resume  =Button((cx-120,cy-70,240,46),"Resume","")
        self.btn_resign  =Button((cx-120,cy-10,240,46),"Resign","","danger")
        self.btn_mainmenu=Button((cx-120,cy+50,240,46),"Main Menu","")
        self.btn_menu_game=Button((16,8,120,36)," Menu",None,"ghost")

    # ── Coordinate helpers ────────────────────────────────────────────────────

    def sq2px(self,r,c):
        return BOARD_X+BORDER+c*SQ, BOARD_Y+BORDER+r*SQ
    def px2sq(self,x,y):
        c=(x-BOARD_X-BORDER)//SQ; r=(y-BOARD_Y-BORDER)//SQ
        if 0<=r<8 and 0<=c<8: return r,c
        return None

    # ── Game control ──────────────────────────────────────────────────────────

    def new_game(self,swap_colors=False):
        self.board=start_board(); self.turn="white"
        self.sel=None; self.hints=[]; self.ep=None
        self.last_move=None; self.status="ongoing"
        self.move_num=1; self.captured={"white":[],"black":[]}
        self.promo_ctx=None; self.move_history=[]
        self.w_time=0; self.b_time=0; self.t_start=time.time()
        self.paused=False; self.ai_thinking=False; self.ai_result=None
        self.result_shown=False

        if self.mode=="pvc":
            if swap_colors:
                self.ai_color="white" if self.ai_color=="black" else "black"
            else:
                self.ai_color="black"
        else:
            self.ai_color=None

        self.scene="game"

    def _tick_clock(self):
        if self.paused or self.status not in("ongoing","check"): return
        now=time.time(); elapsed=now-self.t_start; self.t_start=now
        if self.turn=="white": self.w_time+=elapsed
        else: self.b_time+=elapsed

    def _fmt_time(self,secs):
        m=int(secs)//60; s=int(secs)%60
        return f"{m}:{s:02d}"

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_events(self):
        pos=pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE:
                    if self.scene=="game": self.paused=not self.paused
                    elif self.scene=="menu": pygame.quit(); sys.exit()

            if self.scene=="menu":
                self.tg_mode.handle(ev)
                self.tg_diff.handle(ev)
                self.tg_rounds.handle(ev)
                if self.btn_start.handle(ev):
                    self.mode=["pvp","pvc"][self.tg_mode.sel]
                    self.difficulty=self.tg_diff.value
                    self.total_rounds=[1,3,5][self.tg_rounds.sel]
                    self.scores={"white":0,"black":0,"draws":0}
                    self.rounds_played=0
                    self.new_game()

            elif self.scene=="game":
                if self.paused:
                    self.btn_resume.update(pos); self.btn_resign.update(pos)
                    self.btn_mainmenu.update(pos)
                    if self.btn_resume.handle(ev): self.paused=False; self.t_start=time.time()
                    if self.btn_resign.handle(ev): self._resign()
                    if self.btn_mainmenu.handle(ev): self.scene="menu"
                elif self.result_shown:
                    if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                        self._next_round_or_end()
                elif not self.ai_thinking and self.status in("ongoing","check"):
                    if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                        if self.promo_ctx: self._promo_click(pos)
                        else: self._board_click(pos)
                # Buttons always available (pause icon area)
                if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and not self.paused:
                    # Pause button top-right
                    if pygame.Rect(WIN_W-50,8,38,38).collidepoint(pos):
                        self.paused=True
                    # Menu button top-left
                    elif self.btn_menu_game.rect.collidepoint(pos):
                        self.scene="menu"

        # Update button hover states
        if self.scene=="menu":
            self.btn_start.update(pos)
        elif self.scene=="game" and self.paused:
            self.btn_resume.update(pos)
            self.btn_resign.update(pos)
            self.btn_mainmenu.update(pos)

    def _board_click(self,pos):
        # Is it the AI's turn?
        if self.ai_color and self.turn==self.ai_color: return
        sq=self.px2sq(*pos)
        if sq is None: self.sel=None; self.hints=[]; return
        r,c=sq; p=self.board[r][c]
        if self.sel:
            if sq in self.hints: self._do_move(self.sel,sq)
            elif p and p.color==self.turn:
                self.sel=sq; self.hints=legal_moves(self.board,p,self.ep)
            else: self.sel=None; self.hints=[]
        else:
            if p and p.color==self.turn:
                self.sel=sq; self.hints=legal_moves(self.board,p,self.ep)

    def _do_move(self,fr,to):
        frow,fcol=fr; trow,tcol=to
        p=self.board[frow][fcol]
        cap=self.board[trow][tcol]
        ep_cap=self.board[frow][tcol] if isinstance(p,Pawn) and self.ep==(trow,tcol) else None
        if isinstance(p,Pawn) and (trow==0 or trow==7):
            self.promo_ctx=(fr,to,cap or ep_cap); return
        self._apply(fr,to,cap or ep_cap)

    def _promo_click(self,pos):
        opts=["Q","R","B","N"]; fr,to,cap=self.promo_ctx
        dw=4*SQ; dx=(WIN_W-dw)//2; dy=WIN_H//2-SQ//2
        if dy<=pos[1]<=dy+SQ:
            idx=(pos[0]-dx)//SQ
            if 0<=idx<4: self.promo_ctx=None; self._apply(fr,to,cap,opts[idx])

    def _apply(self,fr,to,captured=None,promo="Q"):
        frow,fcol=fr; trow,tcol=to
        p=self.board[frow][fcol]
        # Move history notation
        sym=p.sym if p.sym!="P" else ""
        cap_note="x" if captured else ""
        note=f"{sym}{FILES[fcol]}{RANKS[frow]}{cap_note}{FILES[tcol]}{RANKS[trow]}"
        if isinstance(p,Pawn) and (trow==0 or trow==7): note+=f"={promo}"
        if self.turn=="white":
            self.move_history.append(f"{self.move_num}. {note}")
        else:
            if self.move_history: self.move_history[-1]+=" "+note
            else: self.move_history.append(f"{self.move_num}... {note}")

        self.board,self.ep=do_move(self.board,fr,to,self.ep,promo)
        if captured: self.captured[self.turn].append(captured)
        self.last_move=(fr,to); self.sel=None; self.hints=[]
        self.turn="black" if self.turn=="white" else "white"
        if self.turn=="white": self.move_num+=1
        self.status=game_status(self.board,self.turn,self.ep)
        self._check_end()

    def _check_end(self):
        if self.status in("checkmate","stalemate","draw"):
            self.result_shown=True
            if self.status=="checkmate":
                winner="black" if self.turn=="white" else "white"
                self.scores[winner]+=1
            else:
                self.scores["draws"]+=1
            self.rounds_played+=1

    def _resign(self):
        self.paused=False
        self.status="resigned"
        winner="black" if self.turn=="white" else "white"
        self.scores[winner]+=1
        self.rounds_played+=1
        self.result_shown=True

    def _next_round_or_end(self):
        if self.rounds_played>=self.total_rounds:
            self.scene="endscreen"
        else:
            self.new_game(swap_colors=True)

    def _trigger_ai(self):
        if self.ai_thinking or self.turn!=self.ai_color: return
        if self.status not in("ongoing","check"): return
        self.ai_thinking=True
        def worker():
            result=ai_move(self.board,self.ai_color,self.difficulty,self.ep)
            self.ai_result=result
        threading.Thread(target=worker,daemon=True).start()

    def _poll_ai(self):
        if self.ai_result is not None:
            fr,to=self.ai_result; self.ai_result=None; self.ai_thinking=False
            if fr and to:
                p=self.board[fr[0]][fr[1]]
                cap=self.board[to[0]][to[1]]
                ep_cap=self.board[fr[0]][to[1]] if isinstance(p,Pawn) and self.ep==to else None
                promo="Q"
                if isinstance(p,Pawn) and (to[0]==0 or to[0]==7): promo="Q"
                self._apply(fr,to,cap or ep_cap,promo)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(col("bg"))
        if self.scene=="menu":    self._draw_menu()
        elif self.scene=="game":  self._draw_game()
        elif self.scene=="endscreen": self._draw_endscreen()
        pygame.display.flip()

    # ── MENU ──────────────────────────────────────────────────────────────────

    def _draw_menu(self):
        self._anim=(self._anim+0.012)%(2*math.pi)
        surf=self.screen; pos=pygame.mouse.get_pos()
        cx=WIN_W//2

        # Title
        draw_text(surf," Royal Chess",self.f_title,col("gold"),cx,70)
        draw_text(surf,"The complete chess experience",self.f_body,col("text_dim"),cx,125)

        # Panel
        panel_rect=(cx-240,160,480,440)
        draw_rounded_rect(surf,col("panel"),panel_rect,14,2,col("btn_border"))

        # Section labels
        show_diff=(self.tg_mode.sel==1)
        draw_text(surf,"Game Mode",self.f_body,col("gold"),cx-200,230,"left")
        self.tg_mode.draw(surf,self.f_body,pos)

        if show_diff:
            draw_text(surf,"AI Difficulty",self.f_body,col("gold"),cx-200,325,"left")
            self.tg_diff.draw(surf,self.f_body,pos)

        draw_text(surf,"Rounds",self.f_body,col("gold"),cx-200,
                  420 if show_diff else 320,"left")
        # reposition rounds toggle if no difficulty shown
        if not show_diff:
            self.tg_rounds.rects=[pygame.Rect(cx-200+i*133,335,133,42) for i in range(3)]
        else:
            self.tg_rounds.rects=[pygame.Rect(cx-200+i*133,440,133,42) for i in range(3)]
        self.tg_rounds.draw(surf,self.f_body,pos)

        self.btn_start.draw(surf,self.f_body)

        # Footer
        draw_text(surf,"Press ESC to quit",self.f_small,col("text_dim"),cx,WIN_H-20)

    # ── GAME ──────────────────────────────────────────────────────────────────

    def _draw_game(self):
        self._tick_clock()
        if self.ai_color and self.turn==self.ai_color and not self.ai_thinking and not self.result_shown:
            self._trigger_ai()
        self._poll_ai()

        self._draw_sidebar()
        self._draw_board_area()
        self._draw_pieces_on_board()
        self._draw_top_bar()

        if self.promo_ctx: self._draw_promo()
        if self.paused: self._draw_pause_overlay()
        if self.result_shown: self._draw_result_overlay()

    def _draw_top_bar(self):
        pygame.draw.rect(self.screen,col("panel"),(0,0,WIN_W,44))
        pygame.draw.line(self.screen,col("border"),(0,44),(WIN_W,44),1)
        # Menu button
        mpos=pygame.mouse.get_pos()
        self.btn_menu_game.update(mpos)
        self.btn_menu_game.draw(self.screen,self.f_body)
        # Logo
        draw_text(self.screen," Royal Chess",self.f_h3,col("gold"),150,22,"left")
        # Round info
        draw_text(self.screen,f"Round {self.rounds_played+1} / {self.total_rounds}",
                  self.f_body,col("text_dim"),WIN_W//2,22)
        # Score
        sw=self.scores["white"]; sb=self.scores["black"]; dr=self.scores["draws"]
        draw_text(self.screen,f"⬜ {sw}  |  Draws {dr}  |  {sb} ⬛",
                  self.f_body,col("cream"),WIN_W//2+160,22)
        # Pause button
        pause_r=pygame.Rect(WIN_W-48,4,38,38)
        draw_rounded_rect(self.screen,col("btn_bg"),pause_r,6,1,col("btn_border"))
        draw_text(self.screen,"⏸",self.f_icon,col("gold"),pause_r.centerx,pause_r.centery)

    def _draw_board_area(self):
        surf=self.screen
        # Board border / shadow
        shadow=pygame.Surface((8*SQ+2*BORDER+8,8*SQ+2*BORDER+8),pygame.SRCALPHA)
        shadow.fill((0,0,0,80))
        surf.blit(shadow,(BOARD_X-4,BOARD_Y-4))

        # Wood border
        border_rect=(BOARD_X,BOARD_Y,8*SQ+2*BORDER,8*SQ+2*BORDER)
        draw_rounded_rect(surf,col("border"),border_rect,6)
        pygame.draw.rect(surf,col("border2"),border_rect,2,border_radius=6)

        # Squares
        for r in range(8):
            for c in range(8):
                x,y=self.sq2px(r,c)
                base=col("board_light") if (r+c)%2==0 else col("board_dark")
                pygame.draw.rect(surf,base,(x,y,SQ,SQ))

        # Overlays
        ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
        # Last move
        if self.last_move:
            for sq in self.last_move:
                ov.fill(col("last_mv")); surf.blit(ov,self.sq2px(*sq))
        # Check king
        if self.status in("check","checkmate"):
            kp=find_king(self.board,self.turn)
            if kp: ov.fill(col("check")); surf.blit(ov,self.sq2px(*kp))
        # Selection
        if self.sel:
            ov.fill(col("sel")); surf.blit(ov,self.sq2px(*self.sel))
        # Move hints
        for sq in self.hints:
            r,c=sq; target=self.board[r][c]
            x,y=self.sq2px(r,c)
            if target:
                ov.fill(col("cap_ring")); surf.blit(ov,(x,y))
                s=14
                for pts in [[(x,y),(x+s,y),(x,y+s)],
                             [(x+SQ,y),(x+SQ-s,y),(x+SQ,y+s)],
                             [(x,y+SQ),(x+s,y+SQ),(x,y+SQ-s)],
                             [(x+SQ,y+SQ),(x+SQ-s,y+SQ),(x+SQ,y+SQ-s)]]:
                    pygame.draw.polygon(surf,(160,30,25),pts)
            else:
                cx=x+SQ//2; cy=y+SQ//2
                pygame.draw.circle(surf,(40,40,40,100),(cx,cy),SQ//6)
                pygame.draw.circle(surf,(65,125,45),(cx,cy),SQ//7)

        # Rank / file labels
        for i in range(8):
            lbl=self.f_small.render(RANKS[i],True,col("gold_dim"))
            surf.blit(lbl,(BOARD_X+8,BOARD_Y+BORDER+i*SQ+4))
            lbl=self.f_small.render(FILES[i],True,col("gold_dim"))
            surf.blit(lbl,(BOARD_X+BORDER+i*SQ+SQ-12,BOARD_Y+BORDER+8*SQ+6))

        # AI thinking indicator
        if self.ai_thinking:
            dots="." * (int(time.time()*2)%4)
            draw_text(surf,f"AI thinking{dots}",self.f_body,col("yellow"),
                      BOARD_X+BORDER+4*SQ,BOARD_Y+BORDER+8*SQ+22)

    def _draw_pieces_on_board(self):
        for r in range(8):
            for c in range(8):
                p=self.board[r][c]
                if not p: continue
                img=self._piece_img(p)
                x,y=self.sq2px(r,c)
                if img: self.screen.blit(img,(x,y))
                else:
                    sym=UNICODE_PIECES.get((p.color,p.sym),"?")
                    tc=(240,240,240) if p.color=="white" else (30,20,10)
                    t=self.f_piece.render(sym,True,tc)
                    self.screen.blit(t,(x+(SQ-t.get_width())//2,y+(SQ-t.get_height())//2))

    def _draw_sidebar(self):
        surf=self.screen; sx=SIDEBAR_X; sw=SIDEBAR_W
        draw_rounded_rect(surf,col("panel"),(sx,44,sw,WIN_H-44),0,1,col("border"))

        y=54
        # ── Player indicators ──
        for color,label in [("black","Black"),("white","White")]:
            is_turn=(self.turn==color and self.status in("ongoing","check"))
            is_ai=(self.ai_color==color)
            bg=col("btn_active") if is_turn else col("panel2")
            draw_rounded_rect(surf,bg,(sx+6,y,sw-12,48),8,1,col("border"))
            # King icon
            key=("w" if color=="white" else "b")+"K"
            img=self.imgs.get(key)
            if img:
                small=pygame.transform.smoothscale(img,(36,36))
                surf.blit(small,(sx+14,y+6))
            name=label+(" (CPU)" if is_ai else "")
            draw_text(surf,name,self.f_body,col("gold") if is_turn else col("text"),sx+58,y+14,"left")
            t_val=self.w_time if color=="white" else self.b_time
            draw_text(surf,self._fmt_time(t_val),self.f_body,col("cream"),sx+sw-16,y+14,"right")
            # Captured pieces (small row)
            caps=[p for p in self.captured["white" if color=="black" else "black"]]
            cx2=sx+14; cy2=y+34
            for cp in caps[:16]:
                k=("w" if cp.color=="white" else "b")+cp.sym
                cimg=self.imgs.get(k)
                if cimg:
                    t=pygame.transform.smoothscale(cimg,(18,18))
                    surf.blit(t,(cx2,cy2)); cx2+=14
            y+=58

        # Divider
        pygame.draw.line(surf,col("border"),(sx+8,y+2),(sx+sw-8,y+2),1); y+=10

        # ── Status ──
        st_colors={"ongoing":col("text"),"check":col("yellow"),
                   "checkmate":col("red"),"stalemate":col("blue"),
                   "draw":col("blue"),"resigned":col("red")}
        st_labels={"ongoing":"Playing","check":"CHECK!","checkmate":"Checkmate",
                   "stalemate":"Stalemate","draw":"Draw","resigned":"Resigned"}
        sc=st_colors.get(self.status,col("text"))
        sl=st_labels.get(self.status,"")
        if sl:
            draw_rounded_rect(surf,(sc[0]//5,sc[1]//5,sc[2]//5),(sx+6,y,sw-12,28),6,1,sc)
            draw_text(surf,sl,self.f_body,sc,sx+sw//2,y+14)
        y+=36

        # ── Mode / difficulty ──
        mode_lbl="vs CPU" if self.mode=="pvc" else "vs Player"
        if self.mode=="pvc":
            mode_lbl+=f" · {self.difficulty}"
        draw_text(surf,mode_lbl,self.f_small,col("text_dim"),sx+sw//2,y+8)
        y+=24

        # Divider
        pygame.draw.line(surf,col("border"),(sx+8,y),(sx+sw-8,y),1); y+=6

        # ── Move history ──
        draw_text(surf,"Move History",self.f_body,col("gold_dim"),sx+10,y+10,"left")
        y+=26
        hist_rect=pygame.Rect(sx+4,y,sw-8,WIN_H-y-60)
        pygame.draw.rect(surf,col("panel2"),hist_rect,border_radius=4)
        clip=surf.get_clip(); surf.set_clip(hist_rect)
        hy=y+4
        for entry in self.move_history[-20:]:
            t=self.f_small.render(entry,True,col("text_dim"))
            surf.blit(t,(sx+10,hy)); hy+=16
        surf.set_clip(clip)

        # ── Resign / menu buttons at bottom ──
        btn_y=WIN_H-52
        resign_r=pygame.Rect(sx+6,btn_y,sw//2-10,38)
        menu_r=pygame.Rect(sx+sw//2+4,btn_y,sw//2-10,38)
        mpos=pygame.mouse.get_pos()
        for r2,lbl,style in [(resign_r,"⚑ Resign","danger"),(menu_r,"⌂ Menu","default")]:
            bg=col("red") if (style=="danger" and r2.collidepoint(mpos)) else \
               col("btn_hover") if r2.collidepoint(mpos) else col("btn_bg")
            draw_rounded_rect(surf,bg,r2,6,1,col("btn_border"))
            draw_text(surf,lbl,self.f_body,col("cream"),r2.centerx,r2.centery)
        # Handle sidebar button clicks (detected in event loop via direct rect check)
        self._resign_rect=resign_r; self._menu_rect=menu_r

    def _draw_promo(self):
        opts=["Q","R","B","N"]; color=self.turn
        dw=4*SQ; dx=(WIN_W-dw)//2; dy=WIN_H//2-SQ//2
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA)
        ov.fill((0,0,0,160)); self.screen.blit(ov,(0,0))
        draw_rounded_rect(self.screen,col("panel"),(dx-16,dy-42,dw+32,SQ+60),10,2,col("gold"))
        draw_text(self.screen,"Promote pawn — choose piece",self.f_body,col("cream"),WIN_W//2,dy-22)
        for i,sym in enumerate(opts):
            x=dx+i*SQ; y=dy
            sqc=col("board_light") if i%2==0 else col("board_dark")
            pygame.draw.rect(self.screen,sqc,(x,y,SQ,SQ))
            key=("w" if color=="white" else "b")+sym
            img=self.imgs.get(key)
            if img: self.screen.blit(img,(x,y))

    def _draw_pause_overlay(self):
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA)
        ov.fill((0,0,0,175)); self.screen.blit(ov,(0,0))
        cx=WIN_W//2; cy=WIN_H//2
        draw_rounded_rect(self.screen,col("panel"),(cx-160,cy-110,320,230),14,2,col("border2"))
        draw_text(self.screen,"Paused",self.f_h2,col("gold"),cx,cy-80)
        self.btn_resume.draw(self.screen,self.f_body)
        self.btn_resign.draw(self.screen,self.f_body)
        self.btn_mainmenu.draw(self.screen,self.f_body)

    def _draw_result_overlay(self):
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA)
        ov.fill((0,0,0,160)); self.screen.blit(ov,(0,0))
        cx=WIN_W//2; cy=WIN_H//2
        draw_rounded_rect(self.screen,col("panel"),(cx-200,cy-130,400,280),14,2,col("gold"))

        if self.status=="checkmate":
            winner="Black" if self.turn=="white" else "White"
            l1="Checkmate!"; l2=f"{winner} wins the round"
            lc=col("gold")
        elif self.status=="stalemate":
            l1="Stalemate"; l2="This round is a draw"; lc=col("blue")
        elif self.status=="draw":
            l1="Draw"; l2="Insufficient material"; lc=col("blue")
        elif self.status=="resigned":
            res="Black" if self.turn=="white" else "White"
            l1="Resigned"; l2=f"{res} wins the round"; lc=col("red")
        else:
            l1="Game Over"; l2=""; lc=col("text")

        draw_text(self.screen,l1,self.f_h2,lc,cx,cy-85)
        draw_text(self.screen,l2,self.f_body,col("cream"),cx,cy-48)

        # Scores
        sw=self.scores["white"]; sb=self.scores["black"]; dr=self.scores["draws"]
        draw_text(self.screen,f"Score:  ⬜ {sw}  –  {dr}  –  {sb}  ⬛",self.f_h3,col("text"),cx,cy-10)

        # Rounds remaining
        remaining=self.total_rounds-self.rounds_played
        if remaining>0:
            draw_text(self.screen,f"{remaining} round{'s' if remaining!=1 else ''} remaining",
                      self.f_body,col("text_dim"),cx,cy+28)
            draw_rounded_rect(self.screen,col("btn_active"),(cx-110,cy+55,220,46),8,2,col("gold"))
            draw_text(self.screen,"▶  Next Round",self.f_body,col("cream"),cx,cy+78)
        else:
            draw_text(self.screen,"Tournament complete!",self.f_body,col("gold"),cx,cy+28)
            draw_rounded_rect(self.screen,col("btn_active"),(cx-110,cy+55,220,46),8,2,col("gold"))
            draw_text(self.screen,"🏆  See Results",self.f_body,col("cream"),cx,cy+78)

    # ── END SCREEN ────────────────────────────────────────────────────────────

    def _draw_endscreen(self):
        surf=self.screen; cx=WIN_W//2; cy=WIN_H//2
        sw=self.scores["white"]; sb=self.scores["black"]; dr=self.scores["draws"]

        # Background with board pattern
        for i in range(8):
            for j in range(10):
                c=(235,217,181) if (i+j)%2==0 else (181,136,99)
                pygame.draw.rect(surf,c,(i*(WIN_W//8),j*80,WIN_W//8,80))
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA)
        ov.fill((18,14,10,220)); surf.blit(ov,(0,0))

        draw_text(surf,"🏆  Tournament Results",self.f_title,col("gold"),cx,90)

        # Winner
        if sw>sb: winner="White wins the tournament!"; wc=col("cream")
        elif sb>sw: winner="Black wins the tournament!"; wc=col("cream")
        else: winner="It's a draw!"; wc=col("blue")
        draw_text(surf,winner,self.f_h2,wc,cx,155)

        # Score card
        card=(cx-200,195,400,200)
        draw_rounded_rect(surf,col("panel"),card,14,2,col("border2"))
        draw_text(surf,"Final Score",self.f_h3,col("gold_dim"),cx,220)
        for i,(label,val,c2) in enumerate([
                ("⬜ White",sw,col("cream")),
                ("Draws",dr,col("text_dim")),
                ("⬛ Black",sb,col("cream"))]):
            draw_text(surf,label,self.f_body,c2,cx-120+i*120,265)
            draw_text(surf,str(val),self.f_h2,col("gold"),cx-120+i*120,295)
        draw_text(surf,f"Difficulty: {self.difficulty}  ·  Mode: {'CPU' if self.mode=='pvc' else 'PvP'}",
                  self.f_body,col("text_dim"),cx,345)
        draw_text(surf,f"Rounds played: {self.rounds_played}",self.f_body,col("text_dim"),cx,365)

        # Buttons
        pos=pygame.mouse.get_pos()
        again_r=pygame.Rect(cx-210,430,190,52)
        menu_r=pygame.Rect(cx+20,430,190,52)
        for r2,lbl in [(again_r,"▶  Play Again"),(menu_r,"⌂  Main Menu")]:
            bg=col("btn_hover") if r2.collidepoint(pos) else col("btn_bg")
            draw_rounded_rect(surf,bg,r2,8,2,col("gold"))
            draw_text(surf,lbl,self.f_h3,col("cream"),r2.centerx,r2.centery)

        for ev in [e for e in pygame.event.get(pygame.MOUSEBUTTONDOWN) if e.button==1]:
            if again_r.collidepoint(ev.pos):
                self.scores={"white":0,"black":0,"draws":0}; self.rounds_played=0
                self.new_game()
            elif menu_r.collidepoint(ev.pos):
                self.scene="menu"

    # ── Sidebar button handling ───────────────────────────────────────────────

    def _handle_sidebar_click(self,pos):
        if hasattr(self,"_resign_rect") and self._resign_rect.collidepoint(pos):
            if self.status in("ongoing","check"): self._resign()
        if hasattr(self,"_menu_rect") and self._menu_rect.collidepoint(pos):
            self.scene="menu"

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        while True:
            # Extra: catch sidebar clicks before general handler swallows them
            raw_events=pygame.event.get()
            for ev in raw_events:
                if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                    if self.scene=="game": self.paused=not self.paused
                    elif self.scene=="menu": pygame.quit(); sys.exit()
                if self.scene=="game" and not self.paused:
                    if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                        if pygame.Rect(WIN_W-50,4,42,38).collidepoint(ev.pos):
                            self.paused=True
                        elif self.btn_menu_game.rect.collidepoint(ev.pos):
                            self.scene="menu"
                        elif self.result_shown:
                            self._next_round_or_end()
                        elif self.promo_ctx:
                            self._promo_click(ev.pos)
                        else:
                            self._board_click(ev.pos)
                            self._handle_sidebar_click(ev.pos)
                elif self.scene=="game" and self.paused:
                    if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                        if self.btn_resume.rect.collidepoint(ev.pos):
                            self.paused=False; self.t_start=time.time()
                        elif self.btn_resign.rect.collidepoint(ev.pos):
                            self._resign()
                        elif self.btn_mainmenu.rect.collidepoint(ev.pos):
                            self.scene="menu"
                elif self.scene=="menu":
                    self.tg_mode.handle(ev)
                    if self.tg_mode.sel==1:
                        self.tg_diff.handle(ev)
                    self.tg_rounds.handle(ev)
                    if self.btn_start.handle(ev):
                        self.mode=["pvp","pvc"][self.tg_mode.sel]
                        self.difficulty=self.tg_diff.value
                        self.total_rounds=[1,3,5][self.tg_rounds.sel]
                        self.scores={"white":0,"black":0,"draws":0}
                        self.rounds_played=0
                        self.new_game()

            pos=pygame.mouse.get_pos()
            if self.scene=="menu": self.btn_start.update(pos)

            self.draw()
            self.clock.tick(60)


if __name__=="__main__":
    RoyalChess().run()