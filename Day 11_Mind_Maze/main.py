import random
import sys
import pygame

# Mind Maze — Day 11 of the 30-Day Python Projects Challenge
pygame.init()
WIDTH, HEIGHT, FPS = 1000, 700, 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Mind Maze | Logic Puzzle Lab')
CLOCK = pygame.time.Clock()
BG=(13,17,30); PANEL=(22,28,46); ALT=(29,37,60); WHITE=(239,244,255)
MUTED=(151,164,190); CYAN=(73,224,226); PURPLE=(164,112,255); GREEN=(98,230,164)
YELLOW=(255,208,102); RED=(255,111,133); BORDER=(53,65,96)
FONT_XL=pygame.font.SysFont('menlo',34,bold=True); FONT_L=pygame.font.SysFont('menlo',24,bold=True)
FONT_M=pygame.font.SysFont('menlo',18); FONT_S=pygame.font.SysFont('menlo',14); FONT_XS=pygame.font.SysFont('menlo',12)
DIFFICULTIES={'Easy': {'tries':10,'points':100}, 'Medium': {'tries':8,'points':150}, 'Hard': {'tries':6,'points':220}}
SEQUENCES=[([2,4,6,None,10],8,'Add 2 each time.'),([3,6,12,None,48],24,'Multiply each number by 2.'),([1,4,9,None,25],16,'These are square numbers.'),([5,8,11,None,17],14,'Add 3 each time.'),([1,1,2,3,5,None],8,'Each number is the sum of the previous two.'),([20,18,16,None,12],14,'Subtract 2 each time.'),([2,6,12,20,None],30,'Multiply consecutive integers: 1×2, 2×3, 3×4...'),([1,8,27,None,125],64,'These are cube numbers.')]

def text(s, value, font, color, x, y, center=False):
    image=font.render(str(value),True,color); rect=image.get_rect()
    rect.center=(x,y) if center else (x,y) if False else rect.topleft
    if center: rect.center=(x,y)
    else: rect.topleft=(x,y)
    s.blit(image,rect); return rect

def panel(s,color,rect,r=14,border=None,w=1):
    pygame.draw.rect(s,color,rect,border_radius=r)
    if border: pygame.draw.rect(s,border,rect,w,border_radius=r)

class Button:
    def __init__(self,rect,label,callback,fill=ALT,color=WHITE,border=BORDER):
        self.rect=pygame.Rect(rect); self.label=label; self.callback=callback; self.fill=fill; self.color=color; self.border=border; self.hover=False
    def draw(self,s):
        c=tuple(min(255,v+12) for v in self.fill) if self.hover else self.fill
        panel(s,c,self.rect,10,self.border); text(s,self.label,FONT_S,self.color,*self.rect.center,center=True)
    def handle(self,e):
        if e.type==pygame.MOUSEMOTION: self.hover=self.rect.collidepoint(e.pos)
        elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.rect.collidepoint(e.pos): self.callback()

class MindMaze:
    def __init__(self):
        self.score=0; self.best=0; self.streak=0; self.mode='CODE'; self.difficulty='Easy'; self.buttons=[]; self.new_puzzle()
    def new_puzzle(self):
        self.hint_used=False; self.game_over=False; self.won=False; self.guesses=[]; self.code_input=''; self.sequence_answer=''
        self.tries=DIFFICULTIES[self.difficulty]['tries']; self.message='Enter your guess and press ENTER.'; self.msg_color=MUTED
        if self.mode=='CODE': self.secret=''.join(random.sample('0123456789',4))
        else: self.sequence,self.answer,self.seq_hint=random.choice(SEQUENCES); self.answer=str(self.answer)
    def set_mode(self,m): self.mode=m; self.new_puzzle()
    def set_difficulty(self,d): self.difficulty=d; self.new_puzzle()
    def finish(self,won):
        self.game_over=True; self.won=won
        if won:
            earned=max(10,DIFFICULTIES[self.difficulty]['points']+self.tries*8-(25 if self.hint_used else 0))
            self.score+=earned; self.best=max(self.best,self.score); self.streak+=1
            self.message=f'MAZE SOLVED! +{earned} points'; self.msg_color=GREEN
        else:
            self.streak=0; self.message=f'Out of attempts! Answer: {self.secret if self.mode=="CODE" else self.answer}'; self.msg_color=RED
    def submit(self):
        if self.game_over: return
        if self.mode=='CODE':
            g=self.code_input
            if len(g)!=4 or not g.isdigit() or len(set(g))!=4:
                self.message='Enter four different digits.'; self.msg_color=YELLOW; return
            exact=sum(a==b for a,b in zip(g,self.secret)); present=sum(min(g.count(d),self.secret.count(d)) for d in set(g))-exact
            self.guesses.append((g,exact,present)); self.code_input=''
            if exact==4: self.finish(True)
            else:
                self.tries-=1; self.message=f'{exact} in the right place • {present} correct digit(s), wrong place'; self.msg_color=CYAN
                if self.tries<=0: self.finish(False)
        else:
            g=self.sequence_answer.strip()
            if not g or not g.lstrip('-').isdigit(): self.message='Type a number, then press ENTER.'; self.msg_color=YELLOW; return
            if g==self.answer: self.finish(True)
            else:
                self.tries-=1; self.message='Not quite. Look for the pattern and try again.'; self.msg_color=RED
                if self.tries<=0: self.finish(False)
    def hint(self):
        if self.game_over: return
        self.hint_used=True; self.message=f'Hint: {"the code starts with "+self.secret[0]+"." if self.mode=="CODE" else self.seq_hint}'; self.msg_color=YELLOW
    def reset_score(self):
        self.score=self.best=self.streak=0; self.new_puzzle(); self.message='Score reset. A fresh maze awaits!'; self.msg_color=CYAN
    def background(self):
        SCREEN.fill(BG)
        for x in range(0,WIDTH,40): pygame.draw.line(SCREEN,(20,27,44),(x,0),(x,HEIGHT),1)
        for y in range(0,HEIGHT,40): pygame.draw.line(SCREEN,(20,27,44),(0,y),(WIDTH,y),1)
        pygame.draw.circle(SCREEN,(25,43,67),(900,70),100,1); pygame.draw.circle(SCREEN,(25,43,67),(900,70),72,1)
    def draw_puzzle(self):
        if self.mode=='CODE':
            text(SCREEN,'CRACK THE SECRET CODE',FONT_L,WHITE,54,302); text(SCREEN,'A hidden 4-digit code is waiting. Digits do not repeat.',FONT_S,MUTED,54,338)
            for i in range(4):
                x=54+i*76; panel(SCREEN,ALT,(x,382,62,66),12,CYAN if i==len(self.code_input) and not self.game_over else BORDER,2)
                char=self.code_input[i] if i<len(self.code_input) else '·'; text(SCREEN,char,FONT_XL,WHITE if char!='·' else (77,91,122),x+31,414,True)
            text(SCREEN,'TYPE 4 DIFFERENT DIGITS ON YOUR KEYBOARD',FONT_XS,MUTED,54,463); text(SCREEN,'GUESS HISTORY',FONT_S,WHITE,54,495)
            if not self.guesses: text(SCREEN,'Your guesses will appear here.',FONT_XS,MUTED,54,523)
            for i,(g,e,p) in enumerate(self.guesses[-3:]):
                y=522+i*19; text(SCREEN,g,FONT_S,WHITE,58,y); text(SCREEN,f'{e} exact',FONT_XS,GREEN,154,y+2); text(SCREEN,f'{p} misplaced',FONT_XS,YELLOW,236,y+2)
        else:
            text(SCREEN,'FIND THE MISSING NUMBER',FONT_L,WHITE,54,302); text(SCREEN,'Read the pattern. Enter the number that belongs in the gap.',FONT_S,MUTED,54,338)
            bw=min(92,540//len(self.sequence))
            for i,v in enumerate(self.sequence):
                x=54+i*(bw+12); panel(SCREEN,ALT,(x,382,bw,62),12,PURPLE if v is None else BORDER,2 if v is None else 1)
                text(SCREEN,'?' if v is None else v,FONT_L,PURPLE if v is None else WHITE,x+bw//2,413,True)
            text(SCREEN,'YOUR ANSWER',FONT_XS,MUTED,54,470); panel(SCREEN,ALT,(54,491,205,50),10,PURPLE,2)
            text(SCREEN,self.sequence_answer if self.sequence_answer else 'Type number...',FONT_M,WHITE if self.sequence_answer else MUTED,70,506)
            text(SCREEN,'Press ENTER to submit',FONT_XS,MUTED,278,508)
    def draw(self):
        self.background(); text(SCREEN,'MIND',FONT_XL,WHITE,36,25); text(SCREEN,'MAZE',FONT_XL,CYAN,151,25); text(SCREEN,'LOGIC PUZZLE LAB / DAY 11',FONT_XS,MUTED,38,68)
        panel(SCREEN,PANEL,(675,24,290,62),14,BORDER)
        for label,val,x,col in [('SCORE',self.score,694,WHITE),('STREAK',self.streak,812,PURPLE),('BEST',self.best,900,GREEN)]:
            text(SCREEN,label,FONT_XS,MUTED,x,35); text(SCREEN,val,FONT_L,col,x,52)
        panel(SCREEN,PANEL,(30,112,620,548),18,BORDER); panel(SCREEN,PANEL,(670,112,300,548),18,BORDER)
        text(SCREEN,'SELECT YOUR CHALLENGE',FONT_S,MUTED,54,134); self.buttons=[]
        self.buttons += [Button((54,162,220,44),'SECRET CODE',lambda:self.set_mode('CODE'),CYAN if self.mode=='CODE' else ALT,BG if self.mode=='CODE' else WHITE,CYAN if self.mode=='CODE' else BORDER),Button((286,162,220,44),'LOGIC SEQUENCE',lambda:self.set_mode('SEQUENCE'),PURPLE if self.mode=='SEQUENCE' else ALT,BG if self.mode=='SEQUENCE' else WHITE,PURPLE if self.mode=='SEQUENCE' else BORDER)]
        text(SCREEN,'DIFFICULTY',FONT_XS,MUTED,54,224)
        for i,d in enumerate(DIFFICULTIES):
            active=self.difficulty==d; col=GREEN if active else ALT
            self.buttons.append(Button((54+i*140,246,130,34),d.upper(),lambda d=d:self.set_difficulty(d),col,BG if active else WHITE,col if active else BORDER))
        self.draw_puzzle(); panel(SCREEN,(18,25,43),(54,580,570,52),10,BORDER); text(SCREEN,self.message,FONT_S,self.msg_color,70,597)
        text(SCREEN,'MISSION CONTROL',FONT_S,MUTED,694,134); text(SCREEN,'ATTEMPTS LEFT',FONT_XS,MUTED,694,174)
        col=GREEN if self.tries>3 else YELLOW if self.tries>1 else RED; text(SCREEN,f'{self.tries:02d}',FONT_XL,col,694,192)
        pygame.draw.line(SCREEN,BORDER,(694,242),(946,242),1); text(SCREEN,'HOW TO PLAY',FONT_S,WHITE,694,262)
        tips=['Enter 4 unique digits.','Exact = correct digit + spot.','Misplaced = right digit, wrong spot.','Use feedback to crack it.'] if self.mode=='CODE' else ['Find the missing number.','Identify the sequence rule.','Type your answer below.','Use a hint if stuck.']
        for i,line in enumerate(tips): text(SCREEN,'• '+line,FONT_XS,MUTED,694,292+i*24)
        pygame.draw.line(SCREEN,BORDER,(694,402),(946,402),1); text(SCREEN,'ACTIONS',FONT_S,WHITE,694,421)
        self.buttons += [Button((694,450,252,42),'GET A HINT  (-25 BONUS)',self.hint,(61,51,39),YELLOW,(113,87,48)),Button((694,502,252,42),'NEW PUZZLE',self.new_puzzle,(35,62,73),CYAN,(46,107,122)),Button((694,554,252,42),'RESET SCORE',self.reset_score,(60,38,53),RED,(110,58,77))]
        text(SCREEN,'ENTER submit  •  BACKSPACE erase',FONT_XS,MUTED,694,616); text(SCREEN,'MIND MAZE • THINK. DECODE. ESCAPE.',FONT_XS,(87,101,131),36,675)
        for b in self.buttons: b.draw(SCREEN)
    def key(self,e):
        if e.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
        if e.key in (pygame.K_RETURN,pygame.K_KP_ENTER): self.submit(); return
        if self.game_over:
            if e.key==pygame.K_SPACE: self.new_puzzle()
            return
        if self.mode=='CODE':
            if e.key==pygame.K_BACKSPACE: self.code_input=self.code_input[:-1]
            elif e.unicode.isdigit() and len(self.code_input)<4 and e.unicode not in self.code_input: self.code_input+=e.unicode
        else:
            if e.key==pygame.K_BACKSPACE: self.sequence_answer=self.sequence_answer[:-1]
            elif (e.unicode.isdigit() or (e.unicode=='-' and not self.sequence_answer)) and len(self.sequence_answer)<5: self.sequence_answer+=e.unicode
    def run(self):
        while True:
            CLOCK.tick(FPS)
            for e in pygame.event.get():
                if e.type==pygame.QUIT: pygame.quit(); return
                if e.type==pygame.KEYDOWN: self.key(e)
                for b in self.buttons: b.handle(e)
            self.draw(); pygame.display.flip()

if __name__=='__main__': MindMaze().run()
