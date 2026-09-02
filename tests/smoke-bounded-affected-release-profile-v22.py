#!/usr/bin/env python3
# ruff: noqa: E701, E702
from __future__ import annotations

import ast
import base64
import collections
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VENV = ROOT / ".runtime/changerail/ruff-venv"
if Path(sys.prefix).resolve() != VENV.resolve(): os.execve(str(VENV/"bin/python"), [str(VENV/"bin/python"), *sys.argv], os.environ)
sys.path.insert(0, str(SCRIPTS))

import changerail_release_admitted_execution as admitted  # noqa: E402
import changerail_release_profile as profile  # noqa: E402


INVENTORY = ROOT / "openspec/changes/archive/2026-08-29-authorize-bounded-affected-release-profile-v18/proof-inventory.md"
AUTHORIZATION = "d33dab914766b1070d296d5bc69076d259386c15"
TREE = "883b1fb1ca8a68783387f09d55b3144ed419f4f0"
SCALARS = """
000000 000001 000002 000003 000004 000005 000006 000007 000008 000009 00000A 00000B 00000C 00000D 00000E 00000F
000010 000011 000012 000013 000014 000015 000016 000017 000018 000019 00001A 00001B 00001C 00001D 00001E 00001F
00007F 000080 000081 000082 000083 000084 000085 000086 000087 000088 000089 00008A 00008B 00008C 00008D 00008E
00008F 000090 000091 000092 000093 000094 000095 000096 000097 000098 000099 00009A 00009B 00009C 00009D 00009E
00009F 0000AD 000600 000601 000602 000603 000604 000605 00061C 0006DD 00070F 000890 000891 0008E2 00180E 00200B
00200C 00200D 00200E 00200F 00202A 00202B 00202C 00202D 00202E 002060 002061 002062 002063 002064 002066 002067
002068 002069 00206A 00206B 00206C 00206D 00206E 00206F 00FEFF 00FFF9 00FFFA 00FFFB 0110BD 0110CD 013430 013431
013432 013433 013434 013435 013436 013437 013438 013439 01343A 01343B 01343C 01343D 01343E 01343F 01BCA0 01BCA1
01BCA2 01BCA3 01D173 01D174 01D175 01D176 01D177 01D178 01D179 01D17A 0E0001 0E0020 0E0021 0E0022 0E0023 0E0024
0E0025 0E0026 0E0027 0E0028 0E0029 0E002A 0E002B 0E002C 0E002D 0E002E 0E002F 0E0030 0E0031 0E0032 0E0033 0E0034
0E0035 0E0036 0E0037 0E0038 0E0039 0E003A 0E003B 0E003C 0E003D 0E003E 0E003F 0E0040 0E0041 0E0042 0E0043 0E0044
0E0045 0E0046 0E0047 0E0048 0E0049 0E004A 0E004B 0E004C 0E004D 0E004E 0E004F 0E0050 0E0051 0E0052 0E0053 0E0054
0E0055 0E0056 0E0057 0E0058 0E0059 0E005A 0E005B 0E005C 0E005D 0E005E 0E005F 0E0060 0E0061 0E0062 0E0063 0E0064
0E0065 0E0066 0E0067 0E0068 0E0069 0E006A 0E006B 0E006C 0E006D 0E006E 0E006F 0E0070 0E0071 0E0072 0E0073 0E0074
0E0075 0E0076 0E0077 0E0078 0E0079 0E007A 0E007B 0E007C 0E007D 0E007E 0E007F
"""
ACTIVATION_CATALOG_B85 = "c-rl~ZI2sAmhbsh1ig{98>Ta!BOB8L^qq0zHZVP7jC&Ug7zV*2vr24{Oy0~a%bLM__l*--PpV>(8BuDR@s9$!BdwCiV)B>g#EJ9x(|^BRE;gH{>EHh0r=Qu|WxE@iUx&AUc)P#8*sPb|E-o*d<<P9Y`+IxQ|B-*!U+<glmv!HEfBg4$*SuwKSL>^$r&p}xg<7mGtCgtg%Y|uHdbx7dV%c!9Xsl{h%i8E#RBBmsw_F%&S4-E3rMQ$A#<-<_uaE29%D>ZkyKlR}|GE9NYdZgff7-UI>rL~|{zv=8@WKD&ui*!?i+1(-r|M_=dDpC(Wz+jl=KuQgdbb?b?d}f`U+MqFdbt?rUf*t-U)OZ!pTBK>S!}NTPgnk*bj@P<VR5l(-u_|euAA_KzTMq@9dGC*-(Gc#{f9TpP1|30^bPdu-ADgVcH{Tax7Xd$zrovn*{%0O|DAuw-Br^q)|+|PZ2TKG^L^J|uKmZ~f2J4g7ydW=Bw58Ilgd*Vy2Y-)40qoAx>ye1F8bly3;*4$cUN!!haoWI5X`h^rWw~|FcT2WjAv$;D1@1WU}ilt%Q!ECnSx;EJTu4YGLUHqWVJ_DGf{{MVj!6D%0u%Dmt|117}PjX<Hc-g4uhH?YJzcF2DKW48l9~D!mC1#))@W}t_YiALKK1x!zIG$eC-!kh&{qFyds>A*nY_t+wI4j%nidc!s*QB7gd$Q4Z}Mk=-B2Lr%K_5;UW=qaPx~RM&2;oB!Z4^ev#RpxTC>gcuEAF-u&W3F%pO2ED>~mlbjVJZy4SZNs7`hbt#6407)MS`6H5v$cWq9z8T)04Ltf>G2~|S?KdF&coM*T1rNjFCBr_an9DUNaQmG<05|X2c6f%`F~7;(>&_dQqC=dv`NnacirR5vr}HFpAt#t(e$iD?<TwC1N#y7p7ipjTK;O%`8Yt7?jaEwd69Pvr31qfuLU&(qBu4=tgo=bvGixG+a9DI#%`jW{^TkEqZm#{8m$OKUpJyJ?Fv?}`H^y1(Kj>n&LLkgJ^Q+`(h`Yw~{RIlI|KqaV?ibx+XuBT53{uPrqFl$G_J0`P?fb6tH=a4;8>4pC{JPAasHR+(1l64Vwu*3`G_<W+W@B~kVz>OzcC@YbpSK(OEIEs$e7vh7fVIpoBHdmB1j`}7%8JOUI$C5uBe4_^EVU$-RwYX5&~&SHhlO?K?+rx<>!5_KEY;SPV79Iewr;$=l(`pI0SKcbOV=?MYY??Pxmb2ti=jFhZqA1yuTn5(E`S;*5T>cPT2tkxEl?8gL4ru64y8^hJV8Vf;7qAGi6m!I#7pF5KP(0ak>oHU$*Ha;fhUMW3J8gmiV)g5%`*Tal>$gAl}<sLeVjz&#7nfGol-Ir8!sVwoc%ce%b)-HHwdwO5;2)=n#*C<Yz7F=tmjPLJHf1e1^o#0ml+92$T`=<oGVqb9sDF_c91yE0oDU|j<}18zj8mtoda<fyb9b!Y<y<EZLfEb)Wx`wL(r8$n+s)L>B8m{5@0<_akNbi6J^zy(N=%X;%TQXzc15=X&|V=1n;z>!?W_+ZlO3Y*Sp0AEc|1LsflKK)-|Nf?w57f?zYYDIjBbyA|Ac`%$v$nJ13{0DoUsDn-EXWiz8>sZ<JmZBbBSasWY~9V^E${sks65$I}F&=N&JY4wU1_Ce?l$Z^u?hDcdn5!zmO9r)7SrW8Fr>=Y0dj^EOeN9D|PnK|rWEC)V7(vVP2(!?Bi<SjTpxecLTQQ7Oi@M+AP=__w%=0Z_#W5O5cSyB3h1!zkv{9EW-Fm6V#AV0U4hZ3T|~OwB+15}lt)iutO6INl1h<E^4@JPA-Sgj3=OrzYXljK{WBdfR`v9@d-Lrw{Ap2Lut7x9zg91XWWuxnHyGT=zmh6p*i<x_wxccEADIM-`Yaiu!!`Md}iFQNS>cWscDjyP5v?yZ_IqcYk>E?pJ?dZ{GdsKmR)ZdC_hCfBX-S{9=ZCEX|5YA&;e;zkoZT6-aK7wGEJE$?6&?vgb%$JH~lz*nP9^p+t6Sui)J9azlLUl-|$Zc+LFNyZ`)u{{7#-|Ihi~{^LLXZT>HR`j`Lx{kxyv&#pG@1uT6yt?g)T8a)LZsss2}!aO6aV8+-jam`EhdBDXGYTBu5#;aK8$L5?{&ZHncRJjX;nG!bY_#|`6w;n^>8MHoqF?Nn5*s>zxnin3$SFsJobK|V*Bn^(XDdWTrE%ky+2uNVLLnNFR+j7PQ^Q*L_iz=GO%Zh+jM7uEkfBGM<{4MxhY26P!(v~Y9B~P9n%99=RnxMzZGpvmzp))6GM2}7pa#a0|;|H-a=x@J9`?T*BIOY*qK6g}(nzokP(;#bl8d6#;_|Lg2?im0pdLi_h9su{cvp;zP5O;Q}iBL)UAM?-+<V;avXHQ7)><35*mS8Dj9<4B0yUSi^m1`VXrJ@OIm{DbR1ke!!7jpw^8PSdI+upXD{^t9DBwRp2vF9#TpzjJdrZuMVY^b0(L2aXKzy?Q8TiSrhryVP)fBE+xahg3CFa>O>g$J?Kr3xrqD48<sQv`Lr-M8JaSzpYy&9GQ4hQ;icrt7KIBZlDKZm_}3g7QgHJq5GwHKXeRWkhqTrvA<evW?-1v@kl_Ro<BL3)gjtARP`!Y9i|w?MmcW<8Y*gqmH^3>iDoOeMNn<pZ&dELzqf6SQx<3;F>hL)a!Y6*|pn`&F3D8En3N;qg1<*al!2X9@D+MhFOD1ZCqT)miB91ml?Y~jyjZ^-i)0CLarqtH|7=j7s$Ky)rT-j6bLovBB=9N$K=>ZAbd~nXI;~`n_rqT;NSfO&3NP7ghwGhmmZ{>KrDN}1_KWs17Qo#6gcrX;HC=@eO-r#z{VC+`K{pE%Sqo1tLAdy{}ZAOIh?ka<cE<74L2e2azMOPBgLF~<?HzhJig8mU#<kuc*Cppb0m)@*xtPC%#m4Ev6`kn<3uoy@tTnCkq0+NJ7vvmv@_)T!oMHg_N==;<9Njsh$pq@Z-esY`+ONqE>m!xcOKShhCF*gtSOdXbEYj)o3tt9zQ|V>C(Asup{bc)jf704n#6Tl>Qo*)Ic1<Hi04@wq#@(r8IDI&&hK7$=G3$|N;!A=4%t4q9UjLv!7|MSAB|1%OKp(0#A);%cR@I@Ddt0z*MwBW7HVDix12S*WxHyi(0Y4k*>3lXJ5M`?*jj=dJ$5?}+h-!>Y1U6ZOsNlhf-VmBUDhloc+Yd8NX2)4i9VF%4^iMiB#)h6kcR6{At({H#+umGOcZw>Q2_LKMLs%S(V)1pWKRK|DtX13W3)z>Inp-x&8N2e=-+DDus8n~Wz4*v_4`fk+hfFZzl<<*o6Z@F=d@J5{Lo5QrXuDbidf5lkw>3MzL~$dY`Zt}H|yP-Z{EM34IjGp6Nb#*4f|^Sx7VY{Yn4hG$0_s-;0ZN!Ie`}X2DB(sH46xkBG|~Hz{r^b@;8vybx9}I{9|Yjy3&S#3tE_k*a{IgRw>I=wGzrL5!y)8Mb_o&T%<izk3jv!#x@gJe&}Gd?=y29FftkluT+7umeKX(i{ZMTQ%=KA{0}q$)x$&aJUs(mJRIn8dZ<fIvR;`{*d;Iigd07}BPY(PN>l1+Ru{$r$&8z{VcL{#bz#J4?Ff{*I2C;4z5O%j(bqD`17sy$H`}K%KakDVGF_#Ka=1nRH4KgadZ8$5pa{JiRdsyB>D)~z4WWeVkPTI{=z*q>^Jv~}`fus|`*;4ozx}oyJ~Z9Ue|t@~xn4Ej`m^$Gwdhvir~ma1BIyQ6lxxOK`on<15iH5(4yi59AB|A_$a%<C^{Xq_A!X2PVvke0G^#i@vBlXqIS)e0nG~fdSqGtHMc^k`U6tl-a;PCaPg7I@sw}sH)xqtYf?Beqh-&WMh8jZA%AjZ^<GQqsl0*3Hxe5Snbnl1U#gA7=X=+?kMyX$;JL=Pb6o2d4ckp<?6XzJBgR>_AD~xn<5b0DlaEu?YeAZJAB2nHrWP!v}>wwjm0<9mQq+l985k^pO8+*1KAL)KrbVL7X4I`{iGJ`QF3l%U&TS<%EXH2jX1gtTm{6_nR+HQqP_HJ|x%@BgiHuJQtzL^_TtUvG}d@#o#33KYEd^1pFvEOGORl6fBfzGuym|Gb;oeuSF?)@#_{_qgdqZ97Gc=4Iz6Py}2OC8;@@SMF8r|C^_7iL8<#7O-rVvXVcoaZS|=Xg?`W=4~|g$Xzjgp$JuWr(NwHQz=p2VF{2K?)d<A+9DB(}i+G+bu(Y&98Mzf?pQ?!Faa8-+%*{kA1QfW@2sv-f13%%qXimNsh7fGLFF%A~&?wDSEltt-!SMqseU*5a^(vX^hG14t$U`l2GfBHCB;REMJ_{P;mH49v^rG)zSjXcDAE#rv4AnzQj$SH@n`iNLr8xL;4xV?g0K`tMdGe0@jSKN31n<E-ib@1>1UM70CLFm9Kt{!wMS5zu_@UnMNCaCze<{F}2zf!KjwHWQ{FhG<E3i?^ml+MR&1U;mEDTw4gm;DFSCxwA?Bfxee1CXjQLr8#lEsGt7zy&e472F%4-AWjHIw(-Jn`4%hn)fVqrj9*^<-oU>F9B^h7(8xLRZA(TgZ_uRiSirnR5)Bo1!T*xo3nW|#l$(wb5#<{5{;5`}+dK1;NAW&;2xC>ZCY*($f{m_9?txs#)yx7_swyws}w%zsa_J*Iqd!UKW%{}x@0=wUSn^b~yt?_5l8mWeT3b|)9R5K%}DbrY)Xm>&$$C4P5M;-c^Q8nQ_l7RJ$<E+zJ^6aJ32C1}6n1qfmv*o81fJE}=jGXLPQWbInObA&NFgvAVHKSF<%H+Ij+W|lzPbMX02Q&y~JW(jY<N$(6DE<Fq^L^jWo82$#uH9{$9g=`@7y;EP5$uio1A?jlx>lPebl$;Iz#(6dg{x2ns$iMB>eXQ!2@Q0s3&f|g#}@`w_*KXvy>~i$fT0TuZIZG?KaYOmyUU#?W#2NoM7v`jgxB*odY*!XFnByyY9X40ckIrFi}tqNWd4XLcZ3kDvNiI7Q%mk_6?65t-Esw#gYdQR9&ON`9co@xBkRh&3i21EIe;LC&alNA&L(?;A#K60&K8Kz!tAJqVrrV2HOJ;^UR<v?t9jRc0@zj`cNL|U>-m%AHlU66-Jf+9?#rN#haCPh2H<eeF-*B)gEJO4IHN7o)D_r9*MdWAu`c_q)ddTQavWr#`6@M-MApGrs-xQ^K?o#FZYKehfn#*jN&2=HtL=L5w=v&u7CRszJ(HXj|DowOzYwrW1dL-D)wq_CshIPYk-y~I?dnC@_1U`}OvroiE3ay(a_uOHUzQY#pJ$uqa>$=-kWJ2NTPj)plx*npi-1?KT7`ncc*)%~J4CwKC!rBcr$?x@D$`f^gsKIgDr_C7iW;be#&)rOrWJ}j)-3<_WiP75C-mR0cVQOmu=fAt&A<HHU%nzTO~u?+vTTP(J+*3&;yOKKC<|;R7_)}SSU>!tyV@_hzM1{0ySk<lm>=j*=bNW83FfKB7?~iYG|&{L0cb}p;pU4QsyXxIC_GigMy$MSpaMrgM+uD{wTMPk!Vop%J}P)o_K(Wl{t3M@{3=zNAchNxVxO}ZDhx3kXTc=U%v%U`?m`%{4QRD!4QnRRyYb$Ti}kRdH8+~!{NbVtL*FiT%MWcg+kRZFvpz@~40Y<lz*2v4bxG>f=B`fbpiZfWEl^?h1aK~Ma5gkVpf%QULpgUde>eS*wHfMef{m^Jbc@|8dzxg8`b%tkk`ZV2yP$(|s}e_(B%OKhhIQ^rHKgnK)tQ8Z$=e8Q#$s4wh#wE9iWH9fZk>4?14M&{els?H_|)6K`_DI9U2pe21jc8(Rpf?~S0hgabk6vvZD9A$&%iu3cK6{+&pgA%nvkwR!|o$x@yE~o&}_f|b$z}n^(4Y+(^vDtNfE^qo<Y?>kUXtc^CGI$Nc6Y$;?xTxv<G92tvx@*4bfXEv8t;2f;SiSO6ujMS~S|oMXgsC$~F3;S;|Xmm&=QLmh0`l?S{!T^8<HRP1XF`EU)Q<e!)<B6)S)1P}J{+kE7wEghtJN<8c1(hEJg3BLjyTw3mTTqT#b1ABFSFz^Bmg(HKR?>N4nQG<vnCS2IzF?lfrlctwYM${8*LpoIg-*%&;OWdL+=0K;fYQ4GKu4xkKkpo=j;Ih^-}D<Vi8cncv2=YZj%q*Rw9gK$0=9->T!i9(!c9L^2H=^*bHturO~H0S9ALO559pwpmVv?v83oIgg;dC)JW7=&;>89^sPzwm6GGSLj-+%kd=g?`~KQ-lXv(#$Eh?iql`PW5-M%ZDBrqrx#`lCuxL3F&+6jsGr&`N!sS|Hr>|;m^%}(Jh9y>;L%8JNAyfdH08R@7bGXNB1&c^vm`7=3n}EZ9mO-i`^gpOxb$xXU%Teu3ns9{PiA@M+rE`ACIZ|{TV(ip_KS#PYVRp89@Z*t1XZ&zxg$X6FiQ2_#V76AA}U8lvRAj<A+86VY9xN^&b{On{UFyJ8Jg#?`I#HUvIvPvz6WxlqW0Y44KOi7JE5#5V+HnbIzP)bQAQj6~W;>o!gu#W^a`fW~39<w!Pjxhxk~K=Kh5*D*O3u36f_@>U@*b50wC&Ab2`mJxh{QohMbi#-$!S-(0@?j)q@+*EgHX?=Jm6yKKMv@5|Nyyn8?Mx3iiP>2Kc8`u%1-Y}UKxj1NcC;Lp~B|L15=0QcHhFf0C1j{pSqX;xRx4}eb50cdRTF)Lf%rVYAzOXiX`Z`zAz{jlhU{?i&jhHtOK{ZR-9F&&8|ld(+_ze4wmv*9|`x0NGc#d!S!Atuurlk=_f1C+XufqHCHlt1}5?tA}!-*;Wx<xQTSXvL5vSxq%KIr~NqIk(oUW;d*d&(8oomcshQYxD6@QrdtPOjIy=JEtK|u#)qHN$uWg;ZO(M$vjW)pt(}zX;|BSMqk)$anbLQ2u}zXWlOpaq|4LB98w$8d6ronJ$%CpZP)be=9eaWq2;)0Syw4|&)d&9kt(1iOk+Cy!Yc)ORGo}=S_8psF^7zdc+LQuti+RAng-z)ULH(^2$Mp0H50KDBKl^?UhgVYL#Ylv;CQM4GO7_}G$gM2{j-X9N3{E9m%X5BTtSsO2`$8t#=!c86=yVkkeOJCZFbjN|C@&Vy%1({YGba11v!Y3+8`vLMU`Jc-PZh?ZHI)fqnA-V#YzUglG)e@&j!GpddhbklNTntjCJSqcgIJ^W(!_~D1mxa+jt&jns6a#&V}ZMo|K+4#ymNB#-d6kO`ofQLoIPpYe}e$E?#9TM3rqU(Y3aCx_G`zrNf4-nM_dAm;JC9;M6p#FOyK$DX0Mj*&qtClth<TvDG9b#j_vhfBExY{{|<_<~BdF*$h46fl4!)cdc0++qUec!U7w(L<C;DQO@0~=kw?!m`nkiV38T-WZ6k~Pf;T$;i-`2lY+f(n%!)%TEPK#sD`)=5^kA{4L<wdwf3y{`(}rSyT-*GT5rVX8f@160E-#5V#$N{)|p>*UF<O%FdpqFU&t|GOLvo@7B6|YTqhy!2OMMjHXJ#wkouYC+%msP`RXTo!W%Ebp(~~p)g{`xY!BIE)CLiCT@mV}M0}W}gUj`9v4QUYpoO=_a&FObu#0rFy%^K558yrO$i9DNJ_Kp9l9SP`&(8UfbOPX%MwA(X^tKdju+diYc{?{IvOL|OE=!_332FAS$<bs}lWgkv+Tk<r?mUepq-=(Ctpudm%cek+O+&J2n2D9m%XQZevvogTT=ebc`kV_9CxX2>mY(Y1oF!wS39?cN3V62sv_fIq`fsdnP8BTWiI^NrCOWv6y+VdNky58nO;aLE*U0jrM!pXOObQ9)30_ztuVPaumka;nmA{*D-p$45;jG6TC9~&asVSsEZJCt>zt)B6Z-pkt)T~gu1mAxcX4QZ2Z@HO$`mkPp_-4~y(T#dl$KKF)_{V1V%erfK+h#ZX^zMg0{q29h`}zHwwtMp~%(^=BuA~zm2T1Yu&x1{WDnOV{9Bh>_-ssrwLvhEW{N?-<K$FceAp&<%*siV7NK&&>zhoN+JUp3h3Q7Zp(o`O$<xq9v6G38zb`AB&^Gme%a{QGbhOvPT_IkYDf=Yl4BeiHjUqiW3ezCexplFdoL!(~(qGg(2quFfUgXv;{sf#5OJef2YT3DaO9c3wEbCf;1#ctJ~eF10`aEU3)ij=lub*$U*J|P<m?_-w~+%6r?zJ%Qs=*hTA@W49)>olJRTu#74#E<d<;E31E6qsQ71z}8omZ3e_#CN29nCAg<jCz6^(g-ub)Q%?(wkN~x&Ngv(zR&NN^~0hY`cG?w1M~sl*n735y*hq2^ynEI-;?g*{cN|`Hbp%O98eX6M%B&~={q~k`(b(r;$DCI02G&q{|tRh6Q0^I85ceE=_VHPxt~4M`heDa8Fsx3c75VwPylY+;K?m{^?IUv2p-OytG%92I@z7`h^ViC`EgAaUPYxx&%KD#gzQN6-`rNse)Im#cW-Xb`26Sh<cGgpZ<=zR41uQ)w4#T?)n!&vN3nl+)PqzITGO)-J8ldwf#TRB0c`)<in^erm<K@F6_eScXI{|!8y=np{kk{AKMZ$2!P_bPGoiziVahu#S~Mva6zh}B#QOK|9eyCk0DEKZ-B>elnEmO`uhH`;bD4fLmGQJ$M>!&v)L$||lmWD|L(|IC{nc7l#~#a@-SyW0rtI?~-Osc2a0d;Cs<6zjy0r3o2O2lEn*8aSNmu3($vr*>0UmZV6IEbb6}YWphQTalET?R*_ZiFn_WGd*5nqm-&**W};m0r$%X_i=jEUI)5%ZjD{9a6`qXSx4K@3+$z#>e1O;O}10Si}ZaKf_jf3+>nDyz|0QioAj#ZTyd_vYQ~@9jGG%%u8eYhJe7{i0h8Z3k$AIVQacMzdav-j{3a{g~1VQzRK>JFW}chCOR(194ua1FSAN55RL*fxa#^Ux-(ahQGoIxM0E`riBL$G!k_G;d4*l`7?Bnw(x)W+9-^di%tLgaa62gHHR9<aFXJLm{X=SseO)LV!Jz^`Ebz5Ku_Av*<$59g)4xRa!e@=II-HKOav+bfzoVAS2G)Xy#25BK6|YzPG;m}3sp$w;wOfJNGYz7WXTy7FRcKZ={;3sy3#9S&sY_YmtzXAA-uIIS}RX#F_$S~_o|=c8VhC1nPLRapKW8^#NOcC&bns5Su7g_1NvF$H%{bcGa%wun(){4tDJ*t^qMM=a#rat*|a4d(3(ci`9;P$JQm&6FK3^yF_|m4+t~x=ItBAN$M`O;*PGS6Yd<|h_t?PCFJ7BXsJ0f&gRC@DI0p4;il@!yOle9|y)wQT&pCH$n~w9wAP#wv#}j9=#VaK7m8Ljh<#@tM<=VAQ$b-5`3Cdky`J@wUws6TjQcOFzV*F^nSIw@uOHn@&5X=;}CU+GHGm__dDrkYHn<;2tyXdiy02{5qwT>ya>la>?y5ow;UWsf8bCZU+AMo&wRRsR0-oWY+EojTMAlylXB;U+K1G@SA{AW*mtq0(?tOW5v2y*W#q!|=n8~db56q!E(Hueb^xAuOv-t|p4z&r~ab&ID2kTNZEiKn+~I%d_3+X7F`3Jxc)DD=xK$&@J8>!mO~T*Ovr77&*gDpase5nge>q0$;%pmNrAf$?N9?Ij}1RT|)qei<BL)I)F}U5}(if${(6IFDC<9_rRt9|lC~>PCU{f~j+0{q0QPTdQL2E&-^mMX<X>LWRS9$|#ET3RvkC6rxDN3?#l1P<&+&-vn33{00$<>`GYKl{9%Hg)xBWYCw@y!8@tq!^J2fYi^H5;V3kvbAPU=H52t%*C24pQ~Vbl=19!L1ifcin<F%zzClJv4OOa0!Gr(`7EMHY+WVX}S{oFzi|(fLcKEzMUk7C*+egz>PE@dD&O4;&G46moRxiQL!Es9!cq{eF`<D0A#{Ib~b{EJ;7dd4zK{oawm^4T>YvgVWH@bXV<2^kzM^Wae!dwR{t!7e}YJdw+v^?Z(`4h8HKut;`(Vj@#%ABv@j4rw=S9Y-v(LCgFaS`AA0p}1c3Or165^P2n5nKAuHv=?x4$fVgz&-j@jd->a1)Z_HlILl<9_5TBz|UGdWEarNOSjix&s-`X*32rfXmldx$0l0|4pRRR2zm+>Q~Y%kfA}!qZ{m8~#N!nJo{pEO;%$PCxA9%TkfmFeAl-J9?s)WQCb~kEZ5L$QF<rd+)~JYSGC3C&GopBxsxHZ;T8}Q(nn_-2!pbw;IXHJ^19xLy?X`!G0KC2Cl{`<=^?2JkY6iIo5mI5I%i|FdV+X^9U=$<~GQJf8p6OO%ia9+1n$bnr(xc)f=A3)*N(TP=H9CIqQNTCpBok?S0GbO9Ju_LTakp2@y;^qQVRPz1D3Yvr%(%IE6hAK^YVMx_NsobMTEA}YhaLs|&E1Tf`|Dx;^G_C4%x&=3xK|VYOWFlUw;R2&3Fy1_Q-AJ5gp;_tlWmr=CO(E*<15f`)H!Mrlnlj%lE>G8!vs_1&r^odW)9i1fLfFexr7rKfi{8n>j|uoj7B;3kx$X%!}Wdx5>r#qR+tna@hRsfYX{oq&0BvOm|tA)R?p%+c7%TX@{DjwYMEzbzDD)a0LUbmr;{5ph8nt<QbR3UB2<nERR^dVYZ6)nR)L9?#)xw*X>3-B!YZ&eaqv(3wbmuW1=Yx*yvMKHl&X=THFNMc>xzlGWZA`5(5ec#BL3oHT^4OWquV}Pr^Sm{pK@X3P243B$CPW1E#F?a4Wo-R@$!Ay4~qd&z<CLRE|`!>=&=QzqY64%;w0}Xx}3vH`RvE}U;g~pzab0z?flDGvl;rMO&9Xk_tnjFAY+Fa&$sRMZYbvw(6EmHxk-a6c-8z5=wqJKsfdeAJV~9hpu)~y1v#*RHx6G+0gvZ_`x3jvlyo&px{hyPo=Hm4S3y55(J14`Kr@l}82B^&>UuAb`730NZ$<@R;&TcwS7)E|{}teCWcYT3Z=<IRk=WBGL$&lS*Sp0A-k+zdz`yu_9HwojL+2&G*0J8Z`ToP_p6(1ux+St8^Wd0IV2yTc!}P&w5k#5XaMkNE?cOX0Kb8^pDv|rmj}c9DWRqNn88qc4uY#Ilp?tuvHujt~|2utN0O5r;zf`EwOW=!Qeu0`@p+H0%rfZ=3>L{#JO6ao&Y#FV*F5avzz??RtnvR!e4BHAbIYrx`q%CtU-iN(ywwJ5<(tq>;!j%nuH1evtN+$iOTVo(L$cSB#WyeHpYWd}IH*98MMSyIPA=d=iBy_O>$~ADnfDI3TIg@q4QRNz$un2@jzMT^eb*#Dl#m)S3^$c8h%!GdY`iyuQRx#lZM@B_EI<6MW&-06}{n&J~d9$Ot@!!OSzZ3s$oUb5Hf<3vUD`WKG_~cg!RJ$1gmxD@lu%u~CD8k;a_l<xMT@Ed}{+y(fAcM%R0F~YGfaF(Qvg`_I*{wsyRsv)Y*_D{GYeU~{T8rLyC9>>#y0q^mKn9Ur1uDD2Z{=5>;J3PLyN?i}tIkez3D?&{OfjSc#^;@>6Tw%53U6>pT5ncyIHz+I-6yj~fj8oD1f{=3r$<9W=it!g2wl~$(C?uOaOj!`=q3Sr-wgeF1xX$Ipf!%2^%o)0QUzYXT!AwWhijeW{e)$%!I@Jl0)H_HEk)@~f5F_-4fI*ujN09>TEOLVra|{#;%d``5q2dU-`w~BIA*Kp{-WJC!{>eTP4nyW{cJwpEw;^k{(jc%mhGyX$6~hVu6pp}o?|ow&tHs;e@F^_5@tlch=(G2R5fXh*Qa9q3-sM3jP`O&sd)3kzw3H{dQPx+i7;8Fc<;YKX6!<0g<pjznXv_DEJnzxXhC-9f-D1M!;8$HsWC(FF67U+gu1WZ|AytzcKz&Mo6E)ZX87^u2N1$sLklwxPMj3#{u8f0&${Mn-47t8Lc9WJt$1MVY@yjx9JF4@h4d+B;yaX$QaoyK3>oG(U5|nw2QNwMU%c3@P|0%=Y7y@z*{*ls#Bcp%sN}<8%acz?uOPXHqz|m&U7#HuZ5vfQ&gq)-62hx4w378}**;OuOK^Y_W*KOwIL<yT*28|i!s0E!d8?7Pd6jPXL|CVSDp&D+(J)~vaM)s`t#s*z8nzA(t#_P_?xF=I)e;;suLI>$8!UlVi@VTa$*<DAM!UY`jV#V?^p?hB#|eReR*<{UcB!u7Lm*>`;rwFLE<e&=Lx{01!AIt4yTDw=#y<A#W&;+xE+SKuSeqm<N3q8Yruwc!_7SbI!K`7uZD!kc*ADG&y~L2^+f3k7qkFRE&2<1S%giF=7FUo*u(8EGC}15dSQ^3PFQzUNYz+%GbX4Q4=7k=L1!#^?O?iQ$s+bb5R+WeRI8O}Myb_^PqQAt(9Fb)D)&+uzI3x(wHh#QmaDD)#{5~K(Ta!Nr6t^JrOGclNQN{&SPnu(5f*#vq`irRw&g(sZ8`-Z(W?C9_lr;Wlf#0^lKm{Kh+A80v#$VA;gC6QskNq(HMI~8m*E^_y)dB1!D0)4baS0E>rU6y-&}o9TVS>DCCf`8ES6A?$(}Vn3JScdZ?_U0uk7yG7sAid{N8qAt;HV~>3qCf-bm3)LqKM%X9yFCyC-6p-XVBT4b!ar`S0zff#V~C!igmiAh$jwV4oa4XShmhL{_z#aBAe5q5<zwaGlg2yyod-F5tb?mG?~>O*PG2Aqe?^Yf?S`Xl8j46mr^6x9NN03z1b!0&~T^a5}KG0Xra@1hj<oF4ZOhSY=Yr!7%#egiICusxeJtK*_0JHWjRvTWtLA04QhJXprb7_Hae@|YO(x0zv$YJO*fk_{qNgd?=fUqL(8(Io`Ffsy~e(3aI9_p^Os|>U?toH+`7z8M8bfAbwPEf4LYM!b3ZJG>wZ48Vd@#o1WjR}wRh-5l!6^6oMAx)x()(eNAJrhirRvQFFfDO0l!#uF?$>cPD2W5)vip@b=aco$%?vYz%?k?kQ~C}dy~MF&&j)TxtsO|pb1`F(jXMNm|P9#TMQ3K-`(~72Y80}F#&$&T{41e84U>5%;IDS#GpOB`R0!}oR0ij$GST<>;8QERise9(brdve~SfmlnxCnF2iNnZug73pJG1`G&Y(Z2&BBu_~(HmQx@T1C3y6veb!a4DUin&RL2`nA>g)5gpL-Gxc}tex$pfOe&2Ox+)_V@{H@w=eqAE7=ZvSxI+PJ7pw)TkE9h4p+pT8a?wj5G;(E8*G(ggQIsp)YxiCr4!3;GCE!i?iwqiCmspLza5{_ug$+a2z!&lUl{gwU$`l<lxI;0}x>~%ZfQJr6P?e+dJU3oOTb@#%I5IXXkD#18V<>YaI6XKLPf(+hKzv|eMn#<*G*v!IuzVWPSNKdAH<q4LHB(k}SC<hZ!8C;outu<2i&lHpb4Q0q0kRqwFZPPc+$GlaogjBUM9AW(`>#{VhLK9CFKqmCW{=5IUvrW5L^?3`Z!W2*yA_Nk#!+i|Z3H3^O(xtWlQbBb=ox)Y4k<>x|dYGy-OV^;G3_TpAjkk2?H(0XPxaKD9Vro`ZricYGHmt5o6IYAIGSq}BDiADd3$>trT}h2+X^r;l<`GzngbR79sTsFPj1lxNrmt6pZo)b1;X_FOX&V^+^D|J7L45eqj4<jD9yN?tk!62xfBf7J&G!3W*XL^ipTs#W@ibGk1T~TEIj5FKLA`Y(eKFpcpBitREpR6S@Ywj<?N)|`oPGw#Sn$AD#WG&+20*~4J;nKgb|dKD*2P%qWhLvSs4k@u&80JTX)kLjR(!d*Tp3+k?rL6NXdxPID=Yl7aN$;$mlw+gUtZStjMv+J+YOT`=f|*bwu{}cUe5dFhlW01_a#Fzt(YtXA4kKdJU(wg@iOoUG<=*BKhC5q1E7QhNcxkeMiwH03J#zofU+2X8V+FC0x9dd41fj>AbI!vQkTKc!tpc2&-~U|Cchg%2M3V4Hu3n}l3W4SZ~&=%%rCN#Es*1RVJdRNRLth8L!ai0oInWYi4nn*CVuNt^1mZOIB$%gv!F29defo_!ntEaXh7*rnPT)PoI_@;g?GPoDg5t<5Y8ndY8D!Gb5{yNIH!yxgVZlVmx2(^FC!_o<d<@!5Y96r=}bZO?Y0zzaK0HyX9~aYx)6i{&N(9~!Xz_}FhwJTbIwSLG5MvKy->h8XC#H0{9=nyq;TFDN!}T%vnqukoO4FevCuEF7(EK-oKbWvRH_^yg!9dWayVtnAqeN1QRL(Hiz)`;l-XEWqSTft=9gkzG?NA%<%yEIcKAiO(on)37B%%@_Dgvv;SP<4`t=&h%P0*c-09I!zh1xa*d{uw#jsdz7X6Fcfqp%zQMJK@)KhFj>#{iw!UQygG~-ND=g3Uu^w1EBq5atGQif36y)cU3<zmzSe$q){4x4cr_`&u^#|cj8R+b}4YW!(Te0$#E^S(J-6+02-7fn>EQ%zJd#cP>~4`zLhhB;?NSAf!0hVYu$-YH{K>SniWR}CWP3H`S7<gKf~J9f14kGJplRc7t}?!+f`Im?o;q59;M{TN50`SjkQITCivF~5kqU=j9+{TH|LH`7ClvkmPA{HkSX2PFZv_gZpDS+AQ#iejdxd)+TKyX$S<k}IAZnp*!!y)47g=A8L8T1_u@pP>kIJUNz<S;=CLO#WAO{-5}_Llk7cBj0wRY&OHKP~VF=*h3(wkCR_x+aN$$VFKCm3WLWI_UrsDFNr3s<f69zNNfw1Rf#OC!Re7e_^jiB-a@$W{}n%Y;lV5OVdyB^+nIcG+YYMR6AUMW1hZsGM_nhFHc&Cai7-dA_(ZTMQ>>P`_#*FY_R*<;r){KJA{MlhCW!7CXTVLvinpQCXmh{BcGY-$xoH<e=0eI(hki0;%4G^v04qtr2`G)McRD^&yY=7FY~5e3ck3Z{b15YpkST1=nO|WYhEs6^8&5hIPw^6c)^3PpyWQT%;{mWoweo|PW<-%1%GEC47UKuE*i#fIcp|c-SyM$%&6#mfu865PBNLQ!MQmAJfu$%X5$1R1)6BnqzX&xzJ*HS|LC_7VIW?L8G<zyf%A5?U1nqs!-l%C{IiAQ0+KENJwY4v>tMIJkn!Jm(Ws;Xj6V_Vx$5&PxW<`P4a$#1pqEV85jn&5pX7e+sB`9jmc+LD8+XCwCqPx1@HoM{M%YwcJ_6a3_x#AZx;IE24D;08PGBlknWe@L~{(9r3V83ttO@qLm5D3l_vn5L{-u`|&T<<s8D{_fS)lrl%=itMk2$KJz*DL=`&-a_fb7{&)bIzZ<K|a$mD;{RH>wFvfA3P{eLptG@oHJT-Xz@y-otER+MxK@P=4~0R9JP)llKeC)I%ndN;twezj-$Ofs`gevduwKRvD%xLq`g(p-YQ;upS8d91-Mg^1u_?S5uO0eU-$2aO_Ff;Z$0kc@k;)j69{4`3shk?VfQvn*fPPw`b%s8Yvc3e`)0t<%oCiOc>@+Ui7<-jDpb*RL3CZTPR0>kg)O=stw<t_;||fN!b?MJxF7*87cF+Yf>(^fiyW;jM;haDJYSwWr*4!L6IH1jvwpT-2AaDxfxA+#4zGug0KDUi<ULK-qa3m{c=(Eou$c>{Vh>w44gR2HnnRzvJY`-d!A6s2RChKt^<lKWO7obzi!9BOah(Jk@2HI$#h^AY9<gSoezm+G&@RC8)}!T}fPTGd{5ucprk^cVD=hTbj&W{+xSRN(W!JU?Aa0F~+Xmb=di?O)VbOo=&%VMcg}A{cPBYh1q9bqTfAh#OQBSCs%^SJkfqCpceph-1O?|wgy4M61Z85sY*kIXh>&gP?qq<{);4`{7{!0Hj`lyF@%5kCp31&4=6>fL!Z+hFz>B#X6_oJC<k6)ipRW%omig1;R4uqb!$88eP2{|n}lMQK0vSK>g+u}b=KP-03GtO*@0z4)*obH~UH*Jb+6Li!OG;zqMxl=PHF2nrm6ahcy&}Rf>4yw2%4~m;d_r-Yo1ASWv@;f1EA#cE>s}l&r7+nHYc0=P68iH+JcVSV&E<E<ZNFWZf3rkc<4oxs<jU5t4-_~ru=%_hp*Yxe?7mRb1#NL#Nb`o$9K}Pj(NgV`PgY{#NAgfWyhE4~vW~z=(Ht4RJ!CNKke&`{TvmTvXu%IoYwb=8L26tA=kT)b9vocMT*ZsWzyxq_T0}<!L#h9@8gGa<NStavdtvh7){AcV42EljX8PM|8ccM#*WVnzR{sQffbj*HSxHoGy1F+_=L&*;r@gj}=_9KeoH}|p*>}XM(Og+ECj{A;7?!Up6zo)(kRj)>OxxZ-ls_JbKDqg8z-201kNJ)cD?|<<~q<;qVanIZ1H^?UsR9VUzG_-dE`N}5&o#Kbd7;I=%=vN)PIe)34&R07}K|XDVWsO?sB-SWG%u$6nWd8b9I4E~{1X=;Er*$|)X~U!{Q+A(DtONx;R^0fDw3z;p7eMFG8?=@qdKq14iKxe?<c(&`T8*qVvlXge<VD!WP*|8njV$sic*C`d_l9TV9DUhiFwsMr@gtx^C;1dju=F3<-^|%JQF+NDAhEZ6Gj0PJ+x1^#%Rdkj0p%T<=NJ*+e!Odb@n2AbBjty}VC%uZ6)O0k<sFlWxvSk4=~#D&{^KjK-ZvCYVRVtztKRP)9PmMTho;8H#_RnH|Muvz&&!g1J<7h0cGshx`JOxw0{FaVT*!#=muv^I9?FjJzdjJTc@z#2H^-Fw<JV`D?_vcdM>q<>A?@Xph)y`J<xDoz1Y57EW2Xl7L%R<(D(5^kDvI!_a<jZKTSlv>aDuB5a5=gdhhj6EV10+1MUY=U-L%ddG}%@Oq`@Saqe^n{pZZnDH=}L4?P9b3uLeq<Ikr5HjmJ}X2LlYn`r?NjroiM~7|`qJTvh0qN`R_x7doan8BG>Tq(vEG9Q@u1u+Q4pwQ4RG*PG!OW_wI}AHO~)prH_`7A$%c#1~KT*-G#vw38(_XV5Mb@uiTy=-Q7>H^1fAK+(RP_7Q#xi(ct~9%<&oVzpfl{(~HY?T%^fCvT8X%&FF1Ym17rT=UA;+kM*&@i-^=HFL&l$&~hMbQ_gScH<bx6Fea~qYm3~f(XC8yXkv^Siq<5$a&NEJ2KHn+L710zlRTU40e4?bw7E7e2gqnDcX{Gg?f;h26ysFDr?jx=<Wp8IjHOu&{I`*=F~}Nd+JC!`=Y(xtvryMFZCd9b=2N|`VJXE<&v~EW%5H+=uV_M;WU*uT}t;7T*o&g9X{{R*v%D*_fZGpP=pJN+%j6Dqfwh?he=$(6IUi6H?f0WZhH6amhGy6W<Oz^eeTbIuEu9TftFyzJ_Xb2?DM8h-OtkYcR<OH$Oz4wIwk+oD(Y8Je>Rm2S?udk?CWT;2RgI~*u7j-bZ8SiUa2p3pFxCLoUG2t9kEy6es!@;lKe00{6Fz;xb7F5-Srj=_^q8z{lssF#Y`F<l>6hrO?V!pe%;a|x@6@|ori5aLD8SJL;b!i<uK%<l{{a(I471NAF0kaG;+`&JB@OJ13g=$CYWJ1-m7-rzVqo&Bi-g1gC=9lM2EoMo^|O)B4>`wS&9H!RiIW@1oLSIR<^9|Xj{c=?{lu3o{AUK#ByOjc1)NOZ7c!Fl;(U0S>X;$osJh=BYVg^jWvQsmWa|Td5~VeMptV*a@=Guz7v{yXH1#PB+Lkcs~`ne1i=+xJ=&)-)sReOV5*q5MY^kWDQ*l8S`ul=bm?vk4R187(P)mBYJ|PlK<a57^t8@*l=KUTT1cWHP~=yv$p=%JI!LBAFm+7VMOss?l;EESZ5gdX7j8^Bcw@?q##FpeV<_qxQc;Hpf~uG<GfSf`Mp4&6QP)iH!WDImuBg=*DoPM)3`NZ$^XXKG7Ae7uEK*bR>cI$TOuk-0`!#mfJDh^%@aa`vig}tagJ@{T3@a5vNGieU0Vly6UV_KNuqyR1%pvpXR5%SgzY~i>p#m4AXqq4*G-ukCuAW6HdF-AxPlFC7(U1n07D1vlGp@`d@jczg$vcl~zj4!f^q9`0U(<QMcpSjhx*pYfyySzabx12*8&d10Vy1qT=t9a{Ocf+L0XmpOLsq&N9wb^YYhNY$uHpq;qQxlD@zB8}8nOh&$RN=+evbw_dZ|-KFWi(8qZk*AF5=arcK<klt93i7bz8cj23ZAX9I16%Zjy<3wj8b;wO)^Ey?#~e4<83?wQfgi-4>gXB9M#bY_Qg?Wwt6?t($Vyx*e@``)aL!@i>61_0d{SkbE$;4p}*CM{B)imcL5$EoXFzu1ATEhYlvukag28<ftViAmU0id|j;@bJTLqIz80KzW=-%J~aNmp8<U|b>WK_XT-9maj>!yP$PaXuLu8q`R|~=-VD#sJQ}us@&@@3l@(1UklZo@)In$((Z@N$sDx=A9Iesw;KsY2-Q4xrZn<f+Pd4PtoH<u%&>!qgD8vuV|AVIQ&rq7tC040J)8}Q-=RDB&7X#%Ji^0xOH*-#{c_o+e9r4j5yA)}bqco=wzxNnG5Eq3I*CTPwlrCJxMR~THKZytW86U_G`B<7?o8|TJoKy5@3h{%NMsXav>)#Kfs9436*V+bXD8ea-6C5dd!VE^2UrlV(V$+=Q@RF%GM}0f%)>j_}K(tyUvCUslIi8@(AgJDCcBR1-craCfsThY!#Gi&!;%=r?{Vb(pt}abRqe4!3!nKryNtfs*L|cDWTkpG;z6$@>v#Vy9-}27fgh~iL<w{?q(Z`c*K;z1dvhB5ZY)tWn?d-3M-NOG?G<oKz^6W-=jwg;M&w%!IJ<4+(J?8Q4c9i4U_rEkdxZPQxO0(x(C-KIUW(g<FG(X!*v%k358n_=uqx*-p-FzQzy@lJMC8$h$+(IT%$8wTP=tPqzUp`8;Vznq;XXD0~q+r}Ix<u>l=0;)9`s<7B8qOAb5`>~Z0pgb~2|uKexBh$U8$>ZzqnO7l^8&>DjykfSt5MJk-_3Ca+>F+miJx&beDI%{{sPXY@<^}|nb%3o5oH=L>LJI7roTi_z4}{_X;8Py9dJ;wwxeUk<~#rDD~dH<@I#Kl%!D))U|al-HnI)wXr4;e`A0AFm>wvoKx3?^%ZyZti7GL$*?+hmR{pyM5bi?-G(}`1snM(IFVXSs9O|gjAAnn%Ep&pMHJhPF)B$>=uj5-i7eYVOa}a(w^rIWbUvzQ)bi5F#a#RMOO3Xpicrfb#vo5ee$H2kV6~WY1zAz6|D)+;p8&04+)@=9g^%>Qi>rmfnI1@ODfzvoXZY2W7RR=@JUsP;0&YAnR(&*0otFD@G+?n<MRvJ9qb-*26pwSQQe%3cIz!SQLWJ!GVVr#0?C{=SGIN*Xo9_uvxB|1AW15d`wX+sKj&8SWzfjO{X3oyYpW66fU2wh$%%E5-8jH2+9@tZO)uU*iCaRv`3QTabE+wFeQErz!1F`)~~=pyYa_51l_C#H?%%9^5z{-TTP?&jcon3&OPVv>&0WQE|!GIV}`2Q1P!W0_y5{SC~Rxtm~zA@Rk_$Tl^Z*G}YnYI^bJ%V9TPJD!RC#l|+j{<K)b?7bX(@AZ5s3pW8XmTpGX(RS=xVEu_W)@SYSpY8=rko|Q%_&31gEDWQIRi$snz?<@zN$oExws775_4=1)wr}@<5{<n@djne~LB|zsz>QjtqAi(;4OToFvjQsKs0FT`xX?-9am5?Y2WH2XGyYOu_WW~{@p?bnvDV3741YaMbJ$WCYevo~r|NT0@O&|BaBJK$Q6-^A6mh_fdd%cah-x6EkKFTpoJNA3Jml#sQtXat^Gg2_eSw)o<Y5~gnA_t0D+1SbT8}1M&6F%TnTW^FaL$#tNaKxZr=i+wjt9BUISb`0a0cWmLvoR3wk{bf>UQkZc+86D`?jNBhO!+$*oG0)5<F%KZupB<<({V=L7pwTs~#|f=_xBY!Y;NNL%>&MxG~0&qPcPUxjl~?^EBmYOPK~8DBzLM%pz0VHW=Tw!0uo!vXMomfL#EbaYfEo1q^t64z)RT#Z>elv)%R9|E{4yRM>YN)vuaea~H+JJbKkk)r>C27U@BG0v|8msOCY+Gj@`FRW&YQ4_&ng?y_1kqe?z>9YKz1iPu!Tl>{DFi=!Il_2?6SRp(Dg!>aYsmsXeVOPhcmRK1UWwUh_oe)<*2h#dbMT&{PEO%V>&dQ3B|U71xsUx3CRgr%y`O@l5)_DVU9o8#f;BW@m@Qi`>&pW+Uw+X=hSN%TR^Z1>m!MO!fE*&1d|;Uf(nfi5BtuBuSSOBbn%-pC&SFTs8@BlZNb2i?$*^9L1vL&E@4o`U>^zs8ek%M_#4iBd!4bur=aKwAggroeh24!9-LI8x=0*|s>33I{f{C~ryeikYfdJB!2HQ8h(9QYeGyVpP8;=Rtal*2%EZYT`;>?F77t${9Q~O_=Gho3k(<m@3^}@8<i>V)qQ?V}srwzBHfVc8VKTF(nmJEyqcUr&VySG{;kqV>&vp=x=Ae^7k{|_PMIz$!Je$-FyKHlSsI0de5twcWpcLxfABFgzF%}HBu+oiA)8aLKYR#^sA1xiEquq%mr1T3aW?7)7a)OsS;39d5~1YVg;3?B6As)w}GDfMxNB!5s$HC!duAxVr^+6t8h;}g38sEsF{w93jE!F+}Y}SyYIj0ueaMp_nEz+!B+E+&FB7)e<KIWo4&d2X#2-+-m!P=&AUImd(YnZH)%i3cZ=O0|4cXke%9=k?JE22TA`ny{KFEq?H4^QXq0C}6&|>X9i8*z?K^(ob^g1^ANrwOtmfAx9COJ7bAPc&lQt%T26R(PLDspH(djv7-6(J}&#}?^@%HNZlC_Lhu8Y>r8eAjGQ6tNI6YQRe7cN%Y_256tG05hGMt<@h`2>Qcr2wL;^9>-bw|jr&OQJgMNS!m?5RLGw!3qz@;N`e@RR~Y`6**oU$9l>sIB((<Ku$moB+&v`qC*(Nuh9X=JAod;ZJ<cBfR|`a1HhAzXOt2WgIvNR58e<Z&~ij#AS+-UE(2Z}ZFJ|6G!jP{U6e<^NCIpiS=PX^tb#0?_=%zCo>vkFI3d9#XX=_s&FJC;So|plJFweRh4ui-;RU4P08fof<&E0IrnUa9(u=alCQ5x!#sOy)v~J*hd}17CiqT8aPtG@jcnVC78`+M05+;YZa|S;qoF&)>F9a={x>{8i)rvQ~SvhIyMqcWrFqhRrR+qI_dbzY0p0}yBu*>>VHY-&r)3`;=<*|_HKWzihe?Cn3m@a?#%JX5k{IK4v<`-T2@ew`2DkgsG?tQ--IF18OQ5pi{g-D#h0jE7U?YGJ@z)2i%)H%Qu15V+9ql_)f>N2=#9B$5Yb4(Osn;0B$wFg%-Zpr{>alrA)lk-a{W~Bo{#|a&0+?Ii^20}-NaB3%46><s(@}F=?>|`;=0uJOt;p9W{ix8Qzdzy)I0v?bXB{cG*DHNs@ctEZcPDgUT@M7Qrxl=fu%l+~j7r_0F@PK?OoX+Nc$@Z8K4G+k#BItN7=zpca1M;m1I-m<`)KLmNAn%F@adJ`6Q31%mBIu0nmuwA|1DzP=yX)=6IG5@`wEXBSjr&)gQ9q4m;Yr%_q{-J{IXD~T1ic9}Gcuz{Wx7(t*WC}F_b<*0{(3AQ56PH_aZ1v7en2gwwqvmwzyB{K!G4uI&)*;Gr0mYzzzTASCWz`8n>y2gB5j&fQR^2GTOohBX%|E0f_b{9Nq#iBOu-3Y0|_9Zq|#Wa<11sg{`;A&`^)uiJ>+f-i5p|+rZCoTo~{3=i`@zdGv`dw9$KntBtT6g9ZaKm2|jB_!m{0NZ{+U)(xdwK!ArB?N3jo8=bKS_a2q|vZ-Or&Gmc{yKhBJTawbd#`FI08;aA8Hu4Sr<cPxB`J_BdQRsgcqhTs|lXc|psJk2)BjqNysAYLn<v)^bMQjWB@hE{um2~(bpgk<ZEJ@p(DwnUDAHm{<YUz%A_pv_y1?W@KXDopTV?IU<QNmK4@f+QnpW+;ovkY={b*zyjn_dF-1IOIo`)UjbAwxQK}XtrOerQJCqKHbqSN7Oo?cE#_!9ChclVdqWI)LqkGZ~Rlg-#7ktK`@^l6p<a^Fc&%g%=>n@-fyy3)Dn+p9roXh19pevt)Dt?9n3fD@H-CyJyz%W=+!w;)KofQs%RtXoc+QR7*23OWyq4eikkkH-Whu9zlg=v^MmFeH;n!V4W9qUsq2V`<7P_0iDOfi&k3*SL5Z!-|B4Nv&kgXT9?&_nmQbOF$&fjiir1v#4bxEWtO%NuJXu+CwahQkW5@qjc&{_}aK!MP=G@4Tu%Qf$1kr`Cv;~+Nrg=Ml5z)m0&9?16|FUjA0Z8ivA61rUIZt5=VlbikH=LK$QvDmKevX<s<`)^OecOH(?iN7zK0d^v0p>}Bp`;e<=xV54e9oHqP`IGku7_uE9_uN1_qr^=QG*_%n2k+)d-#x^t;Rh{aI%igiYHY%C-6LPLEO=II`6M9{MWgEwgy%o70Ltekp<8&LPax$)ADmV&j}W8wp_#6#V@h(yd|ZT_p^Wb*MIxBGgiE@gikBsd^vNT0vbqwIivvBB)~ONU&>gn0+Fkw5_ij)mc??FkX)&}(k~LK_#=|6f+S0+Q3)opzq{qIfia@gwD@_(lr8g%DEA<wkPk$b%54226AwgJ%`k7eZr36SH2Uet^X4Xr`hWa*=6NxRu=%O%m~2sp7H%oqblcDRp=*F~k5zq;$7By&)B(E%@<^{&&2Cr^pP!+8Z1Bw&ugzhEcbElTGYw>Soy7OJ5dscQN0C~;=-7bY5B`h#=JMTl`>tJn_uu>V>VLlLhsE&j{mkFOY92tJt#*zEe$wK~54+!eQ@O)|omLT&D`Qy~r>Z%UiY9-SU!oI`yTzwjcey_2Lix!!;e=Dtobd#z=k0%<$WtJRC#Bf9gmY{b<vf#tPAulh4Q}vKIIMh|iA*JukQx$F6Q4%z_t2l{6E$!C?>FKPKhOI8W}W}RM&j+Kh9>hQ5Qf-K6_Th@y`4+Qggfi9=gA-^1#R;~YMHa~lLU}VB!y}sxnLqC2<&>7|4yoJJxI-F=&{@mHN|56DtYl-1r}E+i7QkDZq@Y5X17}GhW;6{_87xQFV7*8T2nVS&UwD`xDOmnr(m2Agv${pd3pV!q4H6u^W<ne$t}n$&Wucntd4=zckgHGq3KrZGd6!?5Qn>g<IF81+7(nJH5%)*7;4UhWmT$b2HkQsbF4N@#7eHW_q)%t-D2C!*1hL-&K}_u%%czL^f>4|nRCtjDs_ogGe@<yEQzvZD!OmQ-RT`jf+wU)<jI&sHv#flJEYR_P8j}@CuT8XF5KJ_Xkck5NL@#pTUa}<1f$9;${?pz#X34JKF{}y&Tqf7z8O}{<>GoXd^7%pz4__q_h&!mC!W57+?mPE<<gv8hn@jM;IQ72d-keGy)NMNxd@JH!K5pZC*J-n15X*9eS>08D>$Mdw8Z0!w=g7Bfx4r4rNd6D<EPyIpX<h(82fgQU^+$gxyY0<w@H|B6f&k0npZS{JVi0TrBQp$3Q2k)gZ)HUkTsPsmFxbbd({kpq%pnGgj({ExWOD&okSdZhqhFkOPAOn@r@ydOPqrecO!8JHaasMG@e_l4v15Xv$HNNdkNx6wPv}(_Qx!LiEf&aMakKVpiiqp%MrU5ZXxpaj2)_N=@;APRNaz0rmvs8K^`<!C~z^%00ow&v7F%G%#^7Pu4^6Nh#`YSy*Rcf4e4wN^EAZgt%KKByT#@d-TJ7+K7ETkh}NWsrG`q}n#yyECeD<rpvfk*3aG$v99a%YmItyTzOv=frgOeqZ6xHW6)hPPr%G^tL8@zsqb#76HI2idHF`2a+t2pv)#YmLpZ*<+M2iSBI$z>kCLu@KpCz<VyCBpx6Y6!J{&LVg`hM+#gW6wWn{&S%Z}~>2_swo~^Ch4?1RPhj%TO}o*XT+{znO<_q(HDQ*Z$w5Z{{+jcINCuIph?h(L;v;%cJ}C?d$SDM+0xT(qQ@XN7+rVx$<I2!<n;Yc;IwAiD1O!qO6E29@05f{9tC<Lq9FngEyegcNa}!dvf>8jj*sugaH)q1m|>KFoXLlX9ax7{#p9l-d#UO^C-OsFU<pBu!4*iNQ1M3p5ixQ)69<JXbIKvN6%rsZD!kc*ADG&y*%Hob1KxEy8IK_j~Vg}85r?xyYm-RD21y-bl$Hv*1p}YcezXF1m9nVJgMw61t^y0{jz(R{}Y%7_JpZmjO5prE4g=cyY<xvFuWwnB*&t(4OT#HupvpxuUwYKQ9^MH{fhj`q1;5%NGd3jp;M7D@#zp)7SinyxUi8@Nj;p2BpIhYG~?;V$+}lT9#%tm+pp2tEML?a<}bIfr&rA=#W;a5#x9F!|AuBoMloSa)xiSM!>`BgCH^9K>0q%o*|AB9zc^jGef)^>jn8RHJBtjdOB1MLO$JOujkN=hEon@Gr?_i=X}bQLI|iomJ=HZZL&zc7zh=rs7kNC&cE*D}HFGUD>V}eKl0+L!Yq$Qp>KiOW%*au1#~+<;vj0HjSOUszaAX-85}0CQ_x?{XcoiVt(dQ8#VL0zJ)Wv=nzpF!7kDJW*FU<m=ttbt(cKOcYJ>=Us!EcI_DmRWH_)e>cEr0dzy&T%EpZ)7NE$YXcADpq;oyhmJy3LO=C8H)_&R<+Pl(>c*3tA1-X=V~htPM2eSXj%nE|DbSRvJpHtd8~%=h5momh8m##@SJ((z!IuZBMf`=NFrH`H}t_1T_b=m%{PXuhH><e()c5JG)$Onq7-Vc*10v3`tXeFMo;e|8sNRnRU(8x~E_X2yOu=&^8Ek#@1Hy`A0&Ds|!}M1Fo8#2z6rBY<_%$qrzcT%}!#fpaeCPxBC^W7-SMjjd;9uVZ3}Tm^DSKUj3*yCYT2Hm}zW;zhoQP`6`l&D8VA6OSps#sJpYy_#Z$re0x2W?Uo;FSuwik;tVOB(sVC7z%nGZ`HM|xMDIWD3Q&kq<F}qNd8txhpLZ*ZuLAnE#RV2{RgJ*qs})uuhVq>n6}X8W`*d%OUGGqQ&(9;rRqE7)oY5sZl6cmGkY5HIF!<ms6BISJ`Obv;2Pku>xP)_~GLJu6;~lr4cImnbJ`;bDvE2gqT}xlUY~OA+XxbVu=YvSsNu&|AG*qr-J<cddiCx^8+GjrPXENoeDL>hP4pn1*6{<)PzK4so35RsNoQsXV9#%kCc0D%AN#J{%Zi%OyIlfc79?wiUi}j%*P#S48-!3|Tzw?XcvhAAr<ziTDo}qvA7<}x#a$qbf&MGFj|36UPWi;UlIy-;TRGCJrNhphGcE7B<b~n3f&N#Io8T(1ijR2p^B>LxVp(P^c*pe=Tq|<O4z}6he$P1EoDs-eZ+f(+}+tdZNsGA__hDi&W^P7x)TKxsW6TtQO2=LdP{U`9#nk8{hIIW?JyPTHmkMIBxeSZ<=RoZ_l<mB#xIaf!I1b+L2|L(pSZ~gtu-(G*tqa$AY3<MPb{vdG9=pseJlYowXMyLxo-Q7I}LcX5wA3qDcfb+dK0bJfr`$KV=q3O01UV8@g(dz4mugwFY3~?97RIHC~-fY)r?1Vo_ak3jOKc>MMlfd+>#d5sUXK?CcLV5qnEbxgC3bj~X(-ZV29G`Nd7=j;u)m32>ITA$`C@OF17DiDZQPhDVxu*-GD3K@zv&OHYE{vi=q8LI4evK|>oi{uB==1*if@ZRub1Ca2s(ShnBsa!2`33xnG^jL+DUuB&gO|sz#(*a5MWRI$R~bg1r4T;vU|tkfBzsr#Ah9yq-X)3s)UAgGL{<gt7Ar%GHo8PNxIJ^nZ4_XM2R7tP`c?8mZ6_pOt~7zBjc>>0PdT@J0e)!r=iJ6667CrZ?9CVaH7N5$%t*@E;3?yf@#I%s6>At<By}7d6RKjmWI464R<R0Acv1iZ32Y4{uu24hHAyGgGcWd!gbFLOa+FzFUcSR)xJX`OrADm&QUhj(Ch-+`!mCHhI(h&e(1y#A@|KhhJ8m7VjX|S56Q{T2N11Z>{l!Fw;h#-g$03etYPnHcyZ9NFUbyG}wgxoFc+p(1x&!38Tzi@$8PYnWU-(tW%IsaEHxQY{lT}Yu@+7!8vWk>=p+n+@U$u>vRsY_*Ym^f&$2;nJs+6^w0@oW){zSB2uh8gDnDd?=WoZIsRc!7mQqh180R+Fs77b)Fl_8caoK_a0?NkC_9C<}5579EnE7~}_IG{)wa605OY8{=YiX)$h<;{8w{3LLF(3$~cSH;VF(;;nDTc!%!RQ(sV+B97sHx@cG!X`{QqKgy7x+;#4zB%90pP-<VyU||^FV}@JjXIud!(&%fps)F>R;TNMp8??>^XmLX7FpH#1TIog(1cT!t>W`yfvoQXgrjF+<;LBFQf=dyl12M7C$k^-@tbykKo0_S-ez=BMV2N#oKA{E)dufpLhC=Ea)&SG&Vs6OJ0{2H+~e_3i_ZCaw;ty6XBe9)M)rfZ$b+P#c2=&6&Zs=+Gu2d%h&)4us9%LBl_y8y=|c8o&hmLc(FPO#ILu=ZZ(p7Vz%VYf&N#k*$j+Ta@U(i(i)1ivonqQ0bfsFXhkjTL*Zq8GLnXqpU7fGB8^w33m75oBD*Q~sea1U!1XeupHQ~(SY*HUclHW599wmXrl2<dztHo*p839(HNNOEy-kL|xWjbe@mlVhekjDVtzB~_rG<85$94Y-~62H@1W?me15Jb%s=$O<fsFMaE=f;=zOn;FYXwQtG%3(y6G9G1B#n*}8i7KDe@*+39oZLvpGcHw9(Kc5b&ZBkBOl$^g-)t_=I}aiWES}WbP~25#JZ1bvhA@wawB-fXg)}CAF;$u`>6|l>UqtwnQz<vj(!PjuMn3-+VCP`i{h>&vZOs|<eoWwu#g~pr-t<a3E&a{&ZLf##yRPjJ2>WaE>k@@4r&Chaj>ki3Y5w*;?VjOzw7dP?3-h3-7`2n4Ef*(s={UOy322!yG{N(4n3VDM(tf=^<NV)gBu{4gX2(;c0nJ?~Ign7=Ae1(~lerhl%eMQNw@~sk63XV+X8ARE@+t}FdDqTNfhmB*l2Y#_IS2(@vCK4-(bbN50p{Z|lP4TAJ>k9?`g3kqkb;=QA?73EjB}L|?W4zNffO?rBUHgmY~IUlAs>{~3OK11l=qSX7)Wa4nulZtSd9{_lIE_R`Jjjx&UhOxr6d+?G)p+3!DC3#bdh8u&o4IZ@+19q)?5`F*Wh&WtBkgx{@ivSf4CWKoi)_kVd1l8GxSjVtE2H-bP*0H(00|e*L&Li`=NgZtvd$s@$0i-DL94QgiG=ce_U@i`!iO(lZZyUq4MNR<;%2Yn~QibHa@ibk;gN5k4}^R^3_>jltEl+qBPWm@Ch8JoKiF7N&O+Dtdo4i=dOMusK&<vGGslvCHw`c+fp=SjwZr1a+ucWo|c)^UZo(OR4th)ZE_w<i&Zok&sd;|u?u2c!<JB{Af7ZlJWtq^DlA=eL1hjp{z;^f4X=7Myz2BZdLa=$f8HFLv!eO6v<h9IeT}vutI$TqudxLIcpI|7wWmE_u1CzgNPAkMiLDM|8}Fff<gU+OYUPdj97MN=b6tASl!xvwu@idm6!at1-pm5j)HEzJ@Yc5EGn2%&p+hIBoC8dU;)Iv}=Ev{q09kcZGe3A~9sp~K5NaD=gZc1rJzFt7MKU^&lp9|yNI+>~JkTL`GS#@W<?Pt1z}DN(F2PTA=CjeJF}@2O-I!7WimzryFuGWv-o|s!hB_M^275Hzd;iKT_?e3KR_ey+kbD&<_)So>xp53xH%3N}685*WJ6{bukz?dhH9xi#pf@5qIr;5oy=!L8Zq<KU`|l45vjCG`6$qPH7vuj5Z+G79yC(C!y&mo0l^t9eBJ&Bl`JB%;laNC0w4q?nP=qH^RR8Wj=xoz2R(<A@8WD5P4=zuni=&A7L8k<mQnsT~woF&W9ekinr_glB)bS0ChtKESoo^z@N$HIFA+?Ow=w1gnI#{6U-Fno!@$#CzF)V?!uB}Mx+A7}^r&Njxi6Rda4b#P$KpF{S=uBZ9(=vMQ&XD;&slk1}o~^7IU7{WPIL43$HHPe1vy&jX02<gJY2cbPu;WaN@(!T}T?Kpns~KIiE>;B_P!;UP2`dSr3!s86kP3Do0m3P!TzM+kK2gDU6&hg5*kdMp*k5#AtTMK!%2<ucI9`YWl(9on#-U=a*3lLd1V_A_2Nz0coMqY+t8^WBnv$o>(;x#0EmCT?3+;bg9WS&17V$mMM-|Ix_VC!a*twDumfX|4G%VFzkE*#YSv4aiE!7pN=DJLOv3r!fgz7i;kX6m-VqdLh)O;o{!#qutfmAb6W>X!C(Q6r>OaY{tCAih>A(PeYFRChDHA__0EJxKWOU$ltfa!{L=p~WhRYp?H3Nq#2qYVmKG4<-kP^b!dEUwErEOek($nEcaj_xtP#TT#5gCX_eQl`qcSJR<A^)$oNF}>_qs*2M8RVA2-^+NTZ``Lc87%tmxJL`u<H=K8aiRpaD&9(Lae6d@B!S*|BU><w0{m<(iwYxm;Ej9x2q|G%$!h*7AQsnuJi?XI-<ye|o2F)y^%j@3Gm+f{-sw;OnJw50<ORPMND}aOwED2RXLKU;I>BjTj_4cC4e<Kx$0;(8|Z%@DqAfOUUKy?sM&1_YufJ#IG)#DBtj}<^b6_$XSAfSfn=pEF*#iw2N@~IHz(=Z{Er~=5R#*$AP<kPRw-a-G~%c1T1*}pcIi|fts<INAU7g>!cvX;h`y$JNIYp&M)0AMp2M8GZxvdcF^EnOvBER|dbl6Cwbx{J?4v*^0T=j<iaB1&k@xJ&{IAfgURL^(Caqm|3zNY+>+Lv);0TV6B`E75_AfKo7S%0r128Ra1|>euM@ADK*Ojo|uVg7*Ca2AhtiTw+bqo{ShX?Tpg^4W$h;x^NMGoOT8$zhkt<Uu1dF8vZon42rE`WL8nQJlSnH{s)vCPn?UBC2zr#c%$vbhzW<>25Hs`X-3%#*g|S-7m}O&#l{+5Z9nrLcZH{^IkLufOsF*8+w~5g^=#2y^=NwBpRD-ET)pnn_sqd4*FlpDoo}VbKZr8ozAY-||EDOgDz+M=qhEuo$scI+HD#Y*L6;=r9=v`P@q@?_MV$weO$a7qi!}FLOW(k3-+CD<LE@o3r}Q9DLLQIT`N2uv`#<f=c?=MX1^s>>bV2;KkL;4cH0V9(VB#rOt5>~$6#LED9aHOjc{kxPh#qD=zx2O?J`wyQfLM3xPx4{Ak3Z1+djfXVL9#Z?bEb=YJ=r~Aja7c^#W}d>9JAt8l|Mm^8+Gx-gDOt|e{t>Mb~Der*#XDe5bIvWjYqy_(!475d)8Pbv9b!3U$Z10F-CO7N*<2n{t}&Oext|ti*8tlW}&dETmx_9o;*ch5*~mOgdNNOCdDZ1;&uBzNE@qno0KDM6+f5<+S{TZ4Q5)lTfc`bsFMfU<}R7kj4sjB!tqb%`sv6fyv<!P$&*w-37fmbwCGI;s7lLBbXVP*Nel2YkL;QA{AD74YM;`VM}N$ahSLH{FuFt!cq?b?_YZ>qPFI^ISbo4Np&reEI$ty3AA0V?a^I@arI)k&_8&|e(d_fup3FWanR`vDIgK7y*{ku;pYR}*CH`2hU8REf>x#MPQ(r%{`}tMZUhm7%0LT@wN;BaYU83E7w`sPY7VDv?hoSXfYu{jR430^EB=i?mzgh?}k3<oNM89?T17gY!f@wEk1p~DnJD()9Bf~DexQzk^c@7eeR&GJ)y(!=?;#Kcg1w{SyIGrR#*71NN)=cVgmW97WC+*!erK3-Vf%$U1TWoNJxejea6NVwQJtSmAfi@LEo;Gg&=l>sm?&2{"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@contextlib.contextmanager
def chdir(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def git(directory: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=directory, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    require(result.returncode == 0, f"git failed: {args}: {result.stderr}")
    return result.stdout.strip()


def real_git_fixture(directory: Path) -> str:
    git(directory, "init", "-q"); git(directory, "config", "user.name", "ChangeRail Test")
    git(directory, "config", "user.email", "test@example.invalid")
    (directory / ".gitignore").write_text(".runtime/\n")
    (directory / "docs").mkdir(); (directory / "docs/readme.md").write_text("one\n")
    git(directory, "add", ".gitignore", "docs/readme.md"); git(directory, "commit", "-qm", "base")
    return git(directory, "rev-parse", "HEAD")


def parse_inventory() -> tuple[list[dict], list[dict], list[dict]]:
    text = INVENTORY.read_text()
    sections = []
    for name in ("semantic_rows", "physical_rows", "non_task_targets"):
        body = text.split(f"## {name}\n", 1)[1].split("```jsonl\n", 1)[1].split("\n```", 1)[0]
        sections.append([json.loads(line) for line in body.splitlines()])
    return tuple(sections)  # type: ignore[return-value]


def check_original_red() -> None:
    index = ROOT / ".runtime/changerail/evidence/implement-bounded-affected-release-profile-v22/index.json"
    evidence = json.loads(index.read_text()); entry = evidence["entries"][0]
    require(entry["status"] == "failed" and entry["exit_code"] != 0, "RED did not fail")
    raw = (ROOT / entry["raw_output_path"]).read_text()
    require(all(token in raw for token in (TREE, "diff_fingerprint", "ModuleNotFoundError", "changerail_release_profile")), "RED output is incomplete")
    subprocess.run(["git", "cat-file", "-e", f"{TREE}^{{tree}}"], cwd=ROOT, check=True)
    changed = git(ROOT, "diff-tree", "-r", "--no-commit-id", "--name-only", f"{AUTHORIZATION}^{{tree}}", TREE).splitlines()
    allowed = ("openspec/board/3.inprogress/implement-bounded-affected-release-profile-v22.md",
               "openspec/changes/implement-bounded-affected-release-profile-v22/",
               "tests/smoke-bounded-affected-release-profile-v22.py")
    require(changed and all(item == allowed[0] or item.startswith(allowed[1:]) for item in changed), "saved RED tree contains forbidden mutation")


def check_inventory_and_unicode() -> None:
    semantic, physical, targets = parse_inventory()
    require((len(semantic), len(physical), len(targets)) == (35, 30, 48), "inventory counts drifted")
    require([row["logical_id"] for row in semantic] == list(profile.SEMANTIC), "semantic order drifted")
    require(hashlib.sha256(("\n".join(profile.SEMANTIC) + "\n").encode()).hexdigest() == profile.SEMANTIC_DIGEST, "semantic digest drifted")
    actual = [(owner, [list(command) for command in commands]) for owner, commands in profile.PHYSICAL]
    expected = [(row["task_id"], row["commands"]) for row in physical]
    require(actual == expected, "physical inventory drifted")
    framed = bytearray()
    for name, rows in zip(("semantic_rows","physical_rows","non_task_targets"),(semantic,physical,targets),strict=True):
        for value in (name, str(len(rows)), *[json.dumps(row,separators=(",",":"),ensure_ascii=False) for row in rows]):
            raw = value.encode(); framed.extend(f"{len(raw):08x}:".encode() + raw)
    require(hashlib.sha256(framed).hexdigest() == profile.FULL_DIGEST, "full inventory digest drifted")
    scalars = {int(item, 16) for item in SCALARS.split()}
    ranges = []
    for value in sorted(scalars):
        if not ranges or value > ranges[-1][1] + 1: ranges.append([value, value])
        else: ranges[-1][1] = value
    preimage = ";".join(f"{start:06X}-{end:06X}" for start, end in ranges)
    require(len(scalars) == 235 and len(ranges) == 23, "Unicode scalar/range count drifted")
    require(hashlib.sha256(preimage.encode()).hexdigest() == "7fb5126f7973cc51a27f62c8712c11401ace15b9d40afdf02f1575945dc1da81", "Unicode digest drifted")
    require(tuple(map(tuple, ranges)) == profile.UNICODE_RANGES and 0x11F00 not in scalars, "Unicode membership drifted")


def check_selector_and_root() -> None:
    with tempfile.TemporaryDirectory(prefix="changerail-v22-selector-") as raw:
        fixture = Path(raw); base = real_git_fixture(fixture)
        (fixture / "docs/readme.md").write_text("two\n"); git(fixture, "add", "docs/readme.md"); git(fixture, "commit", "-qm", "docs")
        with chdir(fixture):
            require(profile._selection(profile._paths(fixture, base)) == tuple(item for item in profile.SEMANTIC if item in profile.FLOOR), "docs selection drifted")
        (fixture / "scripts").mkdir(); (fixture / "scripts/smoke-contract-schemas.py").write_text("pass\n")
        git(fixture, "add", "scripts/smoke-contract-schemas.py")
        with chdir(fixture):
            selected = profile._selection(profile._paths(fixture, base))
        require({"python.syntax-inventory","python.lint","contracts.schema-validation"} <= set(selected), "staged Python ownership missing")
        (fixture / "unknown.bin").write_bytes(b"x")
        with chdir(fixture):
            try: profile._selection(profile._paths(fixture, base))
            except profile.ProfileError: pass
            else: raise AssertionError("unknown untracked path did not fail closed")
        anchor = fixture / ".runtime/changerail"; anchor.mkdir(parents=True); target = anchor / "affected-release-v18"; target.mkdir()
        require(profile._root(fixture, target) == target, "valid runtime root failed")
        (target / "neighbor").touch()
        try: profile._root(fixture, target)
        except profile.ProfileError: pass
        else: raise AssertionError("non-empty runtime root passed")


def check_hosted_and_ci() -> None:
    with tempfile.TemporaryDirectory(prefix="changerail-v22-hosted-") as raw:
        fixture = Path(raw); toolcache = fixture/"toolcache"; binary = toolcache/"node/20.11.1/x64/bin"
        launchers = toolcache/"node/20.11.1/x64/lib/node_modules/npm/bin"; binary.mkdir(parents=True); launchers.mkdir(parents=True)
        shutil.copy2("/usr/bin/node", binary/"node")
        for name in ("npm","npx"):
            (launchers/f"{name}-cli.js").write_text("process.exit(0)\n")
            (binary/name).symlink_to(f"../lib/node_modules/npm/bin/{name}-cli.js")
        fake = fixture/"fake"; fake.mkdir(); safe = VENV/"bin"
        for name in ("node","npm","npx"):
            path = fake/name; path.write_text("#!/bin/sh\nexit 0\n"); path.chmod(0o755)
        environment = harmless_environment() | {"PATH":f"{fake}:{safe}:{os.environ['PATH']}","RUNNER_TOOL_CACHE":str(toolcache),"RUNNER_ARCH":"X64"}
        closed = profile._environment(environment)
        require(closed["PATH"].split(os.pathsep)[0] == str(binary), "hosted toolcache is not first")
        require(str(fake) not in closed["PATH"], "fake-first PATH survived admission")
        (binary/"npm").unlink(); (binary/"npm").symlink_to("../lib/node_modules/npm/bin/npx-cli.js")
        try: profile._environment(environment)
        except profile.ProfileError: pass
        else: raise AssertionError("wrong hosted launcher passed")
    spec = __import__("importlib.util").util.spec_from_file_location("release_ci_v22", ROOT/"scripts/smoke-release-ci.py")
    module = __import__("importlib.util").util.module_from_spec(spec); spec.loader.exec_module(module)
    module.validate_workflow(ROOT/".github/workflows/changerail-ci.yml")
    parsed = json.loads(json.dumps(module.EXPECTED)); parsed["jobs"]["verify"]["steps"].append({"name":"Affected","run":"python3 scripts/run-release-baseline.py --profile affected"})
    with tempfile.NamedTemporaryFile("w",suffix=".yml") as stream:
        import yaml
        yaml.safe_dump(parsed,stream); stream.flush()
        try: module.validate_workflow(Path(stream.name))
        except ValueError: pass
        else: raise AssertionError("alternate CI execution surface passed")


def harmless_environment() -> dict[str, str]:
    return {"PATH":os.environ["PATH"],"HOME":os.environ.get("HOME","/tmp"),"LANG":"C.UTF-8"}


def check_admitted_execution() -> None:
    with tempfile.TemporaryDirectory(prefix="changerail-v22-exec-") as raw:
        fixture = Path(raw); real_git_fixture(fixture); marker = fixture / "marker"
        direct = fixture / "direct.sh"; direct.write_text(f"#!/bin/sh\nprintf old > {marker}\n"); direct.chmod(0o755)
        env = harmless_environment()
        with chdir(fixture):
            row = admitted.build_row("direct", [["./direct.sh"]], env)
            plan = [{"id":"direct","command":row["members"][0]["logical_argv"],"execution_timeout":2.0,"cleanup_timeout":1.0,"root":"direct"}]
            require(admitted.validate_table(plan, [row]) == (row,), "valid admission failed")
            bundle, bindings = admitted._open_bundle(row)
            seals = admitted.fcntl.fcntl(bundle, admitted.fcntl.F_GET_SEALS)
            require(seals == 15, "bundle is not fully sealed")
            direct.rename(fixture / "renamed.sh"); direct.write_text(f"#!/bin/sh\nprintf new > {marker}\n"); direct.chmod(0o755)
            result = admitted._supervise_fd(bindings[0], 2.0, 1.0)
            require(result["status"] == "pass" and marker.read_text() == "old", "post-open rename redirected execution")
            broken = json.loads(json.dumps(row)); broken["members"][0]["environment"]["PATH"] += ":/changed"
            try: admitted.validate_table(plan, [broken])
            except admitted.AdmissionError: pass
            else: raise AssertionError("changed environment passed digest admission")
            first = fixture / "first.sh"; second = fixture / "second.sh"
            first.write_text(f"#!/bin/sh\nprintf 1 >> {marker}\n"); second.write_text(f"#!/bin/sh\nprintf 2 >> {marker}\n")
            first.chmod(0o755); second.chmod(0o755); marker.write_text("")
            group = admitted.build_row("group", [["./first.sh"],["./second.sh"]], env)
            grouped = admitted.admitted_supervisor(group["members"][0]["logical_argv"], execution_timeout=3.0, cleanup_timeout=1.0, admission=(group,))
            require(grouped["status"] == "pass" and marker.read_text() == "12", f"group execution failed: {grouped}")
            first.write_text("#!/bin/sh\nexit 3\n"); first.chmod(0o755); stale = admitted.build_row("stale", [["./first.sh"]], env); first.write_text("#!/bin/sh\nexit 0\n")
            try: admitted.admitted_supervisor(stale["members"][0]["logical_argv"], execution_timeout=2.0, cleanup_timeout=1.0, admission=(stale,))
            except admitted.AdmissionError: pass
            else: raise AssertionError("pre-open target swap did not fail")


def syntax_rows() -> list[dict[str, object]]:
    paths = [SCRIPTS/name for name in ("changerail_release_profile.py","changerail_release_admitted_execution.py","changerail_release_semantic_scheduler.py","changerail_release_child_broker.py")]
    rows = []
    kinds = (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.FunctionDef, ast.If, ast.For, ast.While, ast.Call)
    for source in paths:
        raw = source.read_bytes(); tree = ast.parse(raw); digest = hashlib.sha256(raw).hexdigest()
        def walk(node: ast.AST, path: str, owner: str) -> None:
            current = node.name if isinstance(node, ast.FunctionDef) else owner
            if isinstance(node, kinds):
                kind = ({ast.Import:"import",ast.ImportFrom:"import",ast.Assign:"binding",ast.AnnAssign:"binding",ast.FunctionDef:"function",ast.If:"predicate",ast.For:"predicate",ast.While:"predicate",ast.Call:"call"})[type(node)]
                callee = ast.unparse(node.func) if isinstance(node, ast.Call) else ""
                sink = "exec" if callee in ("os.execve","os.fork") else "process" if "subprocess" in callee or callee.endswith("run_admitted_plan") else "none"
                rows.append({"source":str(source.relative_to(ROOT)),"digest":digest,"owner":current,"path":path,"span":[node.lineno,node.col_offset,getattr(node,"end_lineno",node.lineno),getattr(node,"end_col_offset",node.col_offset)],"kind":kind,"context":"public-affected/jobs=1/supervisor=None","predicates":"lexically-evaluated","callees":[callee] if callee else [],"predecessor":"public-seed" if current == "run_profile" else f"function:{current}","transfer":"exact-ast-binding","reachable":current in {"<module>","run_profile","_root","_environment","_paths","_git","_selection","build_row","_member","_identity","_digest","_json","run_admitted_plan","_validate_plan","validate_table","_reserve_roots","_execute","_admitted_call","admitted_supervisor","_open_bundle","_supervise_fd","_group"},"reason":"public call-graph closure" if current != "main" else "seed-incompatible CLI","sink":sink})
            for field, value in ast.iter_fields(node):
                if isinstance(value, ast.AST): walk(value, f"{path}.{field}", current)
                elif isinstance(value, list):
                    for index, child in enumerate(value):
                        if isinstance(child, ast.AST): walk(child, f"{path}.{field}[{index}]", current)
        walk(tree, "Module", "<module>")
    return rows


def check_activation_catalog() -> None:
    observed = syntax_rows()
    require(observed and all(set(row) == {"source","digest","owner","path","span","kind","context","predicates","callees","predecessor","transfer","reachable","reason","sink"} for row in observed), "activation annotations incomplete")
    require(all(row["reason"] not in ("","cataloged","pending","unknown") for row in observed), "activation sentinel present")
    catalog = json.loads(zlib.decompress(base64.b85decode(ACTIVATION_CATALOG_B85)).decode())
    require(catalog == observed and len({(row["source"],row["path"],row["kind"]) for row in catalog}) == len(catalog), "full activation catalog drifted")
    reachable = {(row["source"],row["path"],tuple(row["callees"])) for row in catalog if row["reachable"] and row["kind"] == "call"}
    require(any(row[2] == ("run_admitted_plan",) for row in reachable), "public scheduler edge absent")
    require(any(row[2] == ("os.execve",) for row in reachable), "descriptor exec sink absent")


def check_dynamic_topology() -> None:
    socket_path = f"/tmp/chrv22-{os.getpid()}.sock"; nonce = os.urandom(16).hex()
    collector = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM); collector.bind(socket_path); collector.settimeout(0.001)
    try:
        with tempfile.TemporaryDirectory(prefix="changerail-v22-topology-") as raw:
            fixture = Path(raw); base = real_git_fixture(fixture); (fixture/"bin").mkdir(); (fixture/"scripts").mkdir()
            openspec = fixture/"bin/openspec"; openspec.write_text("#!/bin/bash\nexit 0\n"); openspec.chmod(0o755)
            bootstrap = fixture/"bin/bootstrap-project"; bootstrap.write_text("#!/bin/sh\nmkdir -p \"$1\"\n"); bootstrap.chmod(0o755)
            for name in ("public-surface-scan.py","compile-python-inventory.py","smoke-drift.py"): (fixture/f"scripts/{name}").write_text("print('safe')\n")
            git(fixture,"add","bin/openspec","bin/bootstrap-project","scripts/public-surface-scan.py","scripts/compile-python-inventory.py","scripts/smoke-drift.py"); git(fixture,"commit","-qm","tools"); base=git(fixture,"rev-parse","HEAD")
            (fixture/"scripts/smoke-drift.py").write_text("from pathlib import Path\nassert Path('.runtime/changerail/ci-drift/example-project').is_dir()\n")
            git(fixture,"add","scripts/smoke-drift.py"); git(fixture,"commit","-qm","owned-python")
            runtime=fixture/".runtime/changerail/affected-release-v18"; runtime.mkdir(parents=True)
            boot=fixture/".runtime/bootstrap"; boot.mkdir()
            site = f'''import dis,hashlib,json,os,socket,sys\nS={socket_path!r};N={nonce!r};ROOT={str(ROOT)!r};seq=0;sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)\ndef send(kind,**fields):\n global seq\n seq+=1\n msg={{"nonce":N,"pid":os.getpid(),"ppid":os.getppid(),"role":"group-exec" if "--group" in sys.argv else ("public" if any("child.py" in x for x in sys.argv) else "spawn"),"seq":seq,"type":kind,"context":sys.argv[:4],**fields}}\n sock.sendto(json.dumps(msg,separators=(",",":")).encode(),S)\ndef register():\n global seq\n seq=0; digests={{}}\n for name in ("changerail_release_profile.py","changerail_release_admitted_execution.py","changerail_release_semantic_scheduler.py","changerail_release_child_broker.py"):\n  p=os.path.join(ROOT,"scripts",name);digests["scripts/"+name]=hashlib.sha256(open(p,"rb").read()).hexdigest()\n send("register",source="sitecustomize",caller="",span=[0,0,0,0],callee="",digests=digests)\ndef hook(frame,event,arg):\n if event=="call" and (frame.f_code.co_filename.startswith(os.path.join(ROOT,"scripts")) or frame.f_code.co_name=="_group"):\n  caller=frame.f_back;pos=[caller.f_lineno,0,caller.f_lineno,0] if caller else [0,0,0,0]\n  if caller:\n   for ins in dis.get_instructions(caller.f_code):\n    if ins.offset==caller.f_lasti and ins.positions: pos=[ins.positions.lineno or 0,ins.positions.col_offset or 0,ins.positions.end_lineno or 0,ins.positions.end_col_offset or 0]\n  send("call",source=frame.f_code.co_filename,caller=caller.f_code.co_filename if caller else "",span=pos,callee=frame.f_code.co_name,digests={{}})\n return hook\ndef audit(event,args):\n if event in ("os.exec","os.fork"): send("sink",source="audit",caller="",span=[0,0,0,0],callee=event,digests={{}})\nregister();os.register_at_fork(after_in_child=register);sys.setprofile(hook);sys.addaudithook(audit)\n'''
            site = site.replace('send("sink",source="audit",caller="",span=[0,0,0,0],callee=event,digests={})', 'send("sink",source="audit",caller="",span=[0,0,0,0],callee=event,digests={},target=args[0] if event=="os.exec" else None,argv=list(args[1]) if event=="os.exec" else [],environment=hashlib.sha256(json.dumps(args[2],sort_keys=True,separators=(",",":")).encode()).hexdigest() if event=="os.exec" else "")')
            (boot/"sitecustomize.py").write_text(site)
            child = f'''import os,sys\nsys.path.insert(0,{str(SCRIPTS)!r})\nimport changerail_release_profile as p\ndef main():\n os.chdir({str(fixture)!r})\n env=dict(os.environ);env["PATH"]={str(VENV/"bin")!r}+os.pathsep+env["PATH"]\n r=p.run_profile("affected",base={base!r},jobs=1,environment=env,runtime_root={str(runtime)!r})\n assert r["scheduler"]["status"]=="pass" and not r["authoritative"],r\n assert "drift.generated-fixture" in r["selected_physical_ids"]\nif __name__=="__main__":main()\n'''
            (boot/"child.py").write_text(child)
            environment=os.environ.copy(); environment["PYTHONPATH"]=f"{boot}:{SCRIPTS}"
            process=subprocess.Popen([sys.executable,str(boot/"child.py")],env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            events=[]
            while process.poll() is None:
                for _ in range(1000):
                    try: events.append(json.loads(collector.recv(8192)))
                    except TimeoutError: break
                require(len(events)<20000,"dynamic event bound exceeded")
            for _ in range(10):
                try: events.append(json.loads(collector.recv(8192)))
                except TimeoutError: break
            stdout,stderr=process.communicate(); require(process.returncode==0,f"clean topology child failed: {stdout} {stderr}")
            require(events and all(event["nonce"]==nonce and set(event)>={"pid","ppid","role","seq","source","caller","span","context"} for event in events),"dynamic event schema drifted")
            by_pid={}
            for event in events: by_pid.setdefault(event["pid"],[]).append(event)
            for rows in by_pid.values():
                expected=1
                for row in rows:
                    if row["seq"]==1: require(row["type"]=="register","sequence reset without registration"); expected=1
                    require(row["seq"]==expected,f"registration sequence gap: {rows[0]['pid']} expected {expected} got {row['seq']}"); expected+=1
            roles={event["role"] for event in events if event["type"]=="register"}
            require({"public","spawn","group-exec"}<=roles,"registered topology is incomplete")
            calls={event["callee"] for event in events if event["type"]=="call"}
            required={"run_profile","run_admitted_plan","_admitted_call","admitted_supervisor","_open_bundle","_supervise_fd","_group","_enable_subreaper","_cleanup"}
            require(required<=calls,f"dynamic public/scheduler/group/broker path missing: {required-calls}")
            executions=[event for event in events if event["type"]=="sink" and event["callee"]=="os.exec"]
            expected_argv=[("./bin/openspec","/proc/self/fd/201","validate","--all","--strict"),("python3","/proc/self/fd/201"),("git","diff","--check"),("git","status","--short","--ignored"),("python3","/proc/self/fd/201"),("ruff","check","/proc/self/fd/201","/proc/self/fd/202"),(str(VENV/"bin/python"),"/proc/self/fd/201","--group","199"),("rm","-rf",".runtime/changerail/ci-drift"),("./bin/bootstrap-project","/proc/self/fd/204",".runtime/changerail/ci-drift/example-project","--name","example-project","--kind","generic","--lock-enforcement","none"),("python3","/proc/self/fd/206","--project",".runtime/changerail/ci-drift/example-project")]
            require(collections.Counter(tuple(event["argv"]) for event in executions)==collections.Counter(expected_argv),"exact descriptor exec argv multiset drifted")
            require(sorted(event["target"] for event in executions)==[200]*7+[202,203,205] and len({event["environment"] for event in executions})==1,"exec FD map or closed environment drifted")
    finally:
        collector.close()
        try: os.unlink(socket_path)
        except FileNotFoundError: pass


def check_public_affected() -> None:
    with tempfile.TemporaryDirectory(prefix="changerail-v22-public-") as raw:
        fixture = Path(raw); base = real_git_fixture(fixture)
        (fixture/"bin").mkdir(); (fixture/"scripts").mkdir()
        openspec = fixture/"bin/openspec"; openspec.write_text("#!/usr/bin/env bash\nexit 0\n"); openspec.chmod(0o755)
        (fixture/"scripts/public-surface-scan.py").write_text("print('safe')\n")
        git(fixture,"add","bin/openspec","scripts/public-surface-scan.py"); git(fixture,"commit","-qm","tools")
        base = git(fixture,"rev-parse","HEAD")
        (fixture/"docs/readme.md").write_text("two\n"); git(fixture,"add","docs/readme.md"); git(fixture,"commit","-qm","docs")
        anchor = fixture/".runtime/changerail"; anchor.mkdir(parents=True); runtime = anchor/"affected-release-v18"; runtime.mkdir()
        environment = harmless_environment(); environment["PATH"] = f"{VENV/'bin'}:{environment['PATH']}"
        with chdir(fixture): result = profile.run_profile("affected",base=base,jobs=1,environment=environment,runtime_root=runtime)
        require(result["scheduler"]["status"] == "pass" and result["authoritative"] is False, f"public affected failed: {result}")
        require(result["semantic_started"] == 4 and len(result["selected_semantic_ids"]) == 4, "docs selection bound drifted")


def main() -> int:
    check_original_red(); check_inventory_and_unicode(); check_selector_and_root(); check_hosted_and_ci()
    check_admitted_execution(); check_activation_catalog(); check_dynamic_topology(); check_public_affected()
    print(json.dumps({"status":"pass","checks":8,"inventory":"35/30/48","authoritative":False},sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
