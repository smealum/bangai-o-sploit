.nds

;code is loaded to 0x021622B0
.open "bosnewus.SAV",0x021622B0-0x20b0

; disclaimer : i wrote this code a *while* ago, and it was more or less my first time really doing any RE or writing arm assembly
;		so, this is crap, you definitely shouldn't use it as an example or anything. you have been warned.
;		(that said, it does work, so it can't be all bad)

;in essence, what we do is :
;	- copy some code for the arm7 to where the arm7 jumps to when it resets
;	- reset the arm7
;	- copy some code from main ram over to arm7's wram
;	- have that code load up the main binaries from the savefile into ram
;	- jump to them !

; so yeah a lot of this is actually unnecessary and could be done more efficiently. have fun !

; some definitions (that are really not necessary here but still)
.definelabel REG_DISPCNT, 0x04000000
.definelabel MODE_5_2D, 0x10005
.definelabel DISPLAY_BG3_ACTIVE, 0x800

.definelabel VRAM_A_CR, 0x04000240
.definelabel VRAM_ENABLE, 0x80
.definelabel VRAM_A_MAIN_BG, 1

.definelabel REG_BG3CNT, 0x400000E

.definelabel BG_GFX, 0x6000000

;savefile location
.orga 0x20b0

mainfunc:

	;reset arm7
	bl arm7CopyCode


	sendResetComand:
		mov r12, #0x4000000
		mov r0, #0x40000
		add r0, #0xC
		str r0, [r12, #0x188]

		add r1, r12, #0x180     ; r1 = 4000180

	waitArm7_1:
		ldrh r0, [r1]
		and r0, r0, #0x000f
		cmp r0, #0x0001
		bne waitArm7_1

		mov r0, #0x0100
		strh r0, [r1]

	waitArm7_2:
		ldrh r0, [r1]
		and r0, r0, #0x000f
		cmp r0, #0x0001 
		beq waitArm7_2

		mov r0, #0
		strh r0, [r1]


	;reset screen brightness
	ldr r1, =0x4000
	ldr r2, =0x400006C
	strh r1, [r2]
	add r2, r2, #0x1000
	strh r1, [r2]

	;setup BG

	; REG_DISPCNT=MODE_5_2D|DISPLAY_BG3_ACTIVE;
	ldr r1, =REG_DISPCNT
	ldr r2, =MODE_5_2D
	orr r2, r2, #DISPLAY_BG3_ACTIVE
	str r2, [r1]

	; VRAM_A_CR=VRAM_ENABLE|VRAM_A_MAIN_BG;
	ldr r1, =VRAM_A_CR
	ldr r2, =VRAM_ENABLE
	orr r2, r2, #VRAM_A_MAIN_BG
	strb r2, [r1]

	; REG_BG3CNT=BG_BMP16_256x256; //BG_BMP16_256x256  = ((1 << 14) | BIT(7) | BIT(2))
	ldr r1, =REG_BG3CNT
	ldr r2, =0x4084
	strh r2, [r1]

	ldr r1, =BG_GFX
	ldr r2, =0x801F
	mov r3, #0
	mov r4, #256*192*2
	for1:
		strh r2, [r1, r3]
		add r3, r3, #2
		cmp r3, r4
	blt for1

	waitlooop:
		ldr r0, =0x4000180
		ldrh r1, [r0]
		and r1, r1, #0xF
		cmp r1, #0xA
		bne waitlooop

	ldr r1, =BG_GFX
	ldr r2, =0x02000000
	;ldr r2, =0x214CAA0
	mov r3, #0
	mov r4, #256*192*2
	for:
		ldrh r5, [r2, r3]
		strh r5, [r1, r3]
		add r3, r3, #2
		cmp r3, r4
	blt for

	;change reset dst
	ldr r0, =0x27FFE24
	ldr r1, =0x2000000
	str r1, [r0]

	swi 0x0

;copy arm7 bootstrap code
arm7CopyCode:
	ldr r1, =0x2380000
	ldr r2, =arm7Code
	ldr r3, =arm7PoolEnd

	;super slow but idgaf
	cl:
		ldr r4, [r2], #4
		str r4, [r1], #4

		cmp r2, r3
		bne cl

	bx lr

.pool

arm7Code:
	mov	r12, #0x04000000
	str	r12, [r12, #0x208]	; IME = 0;
	add	r3, r12, #0x180
	mov	r0, #0x0500
	strh r0, [r3]

	bl arm7CopyRealCode

	ldr r1, =0x380A800
	bx	r1

arm7CopyRealCode:
	ldr r1, =0x380A800
	ldr r2, =arm7realCode
	ldr r3, =arm7RealPoolEnd

	;super slow but idgaf
	cll:
		ldr r4, [r2], #4
		str r4, [r1], #4

		cmp r2, r3
		bne cll

	bx lr

.pool
.align 4
arm7PoolEnd:

arm7realCode:

	;arm9 code
	ldr r0, =0x1D600 ;chunk size
	ldr r1, =0x16CD0 ;chunk offset
	ldr r2, =0x2000000 ;dst address
	bl readSaveData

	;arm7 code
	ldr r0, =0xFB98 ;chunk size
	ldr r1, =0x35000 ;chunk offset
	ldr r2, =0x37F8000 ;dst address
	bl readSaveData
	
	ldr r0, =0x4000180
		mov r1, #0x0A00
		strh r1, [r0]

	;change reset dst
	ldr r0, =0x27FFE34
	ldr r1, =0x37F8D2C
	str r1, [r0]

	swi 0x0


; yes, this is gcc's output
; please do not judge
; (or do, i'm a comment not a cop)
readSaveData:
	mov	r12, #516
	mov	r5, #67108864
	ldrh	r6, [r5, r12]
	ldr	r3, =63359
	mov	r4, #416
	and	r3, r6, r3
	strh	r3, [r5, r12]
	ldr	r3, =-24512
	strh	r3, [r5, r4]
	mov	r3, #3
	strb	r3, [r5, #418]

	L16:
	ldrh	r3, [r5, r4]
	mov	r12, #67108864
	tst	r3, #128
	bne	L16

	mov	r3, r1, lsr #16
	and	r3, r3, #255
	strb	r3, [r12, #418]
	mov	r5, r12
	mov	r4, #416

	L17:
	ldrh	r3, [r5, r4]
	mov	r12, #67108864
	tst	r3, #128
	bne	L17

	mov	r3, r1, lsr #8
	and	r3, r3, #255
	strb	r3, [r12, #418]

	mov	r5, r12
	mov	r4, #416

	L18:
	ldrh	r3, [r5, r4]
	mov	r12, #67108864
	tst	r3, #128
	bne	L18

	and	r1, r1, #255
	strb	r1, [r12, #418]
	mov	r1, #416

	L19:
	ldrh	r3, [r12, r1]
	ands	r3, r3, #128
	bne	L19

	cmp	r0, #0
	beq	L21
		add	r5, r2, r0
		mov	r1, #67108864
		mov	r4, r3
		mov	r0, #416

	L23:
		strb	r4, [r1, #418]
	L22:
		ldrh	r3, [r1, r0]
		tst	r3, #128
		bne	L22
		mov	r12, #67108864
		ldrb	r12, [r12, #418]
		strb	r12, [r2], #1
		cmp	r2, r5
		bne	L23
	L21:
		mov	r1, #67108864
		mov	r2, #416
	L25:
		ldrh	r3, [r1, r2]
		tst	r3, #128
		bne	L25

	mov	r1, #64
	mov	r3, #416
	mov	r2, #67108864
	strh	r1, [r2, r3]
	bx	lr

.pool
.align 4
arm7RealPoolEnd:

.Close
