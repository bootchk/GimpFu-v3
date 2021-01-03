(script-fu-register

	"Call_script-fu-soap"
	"Call_script-fu-soap"
	"Testaufruf"
	"HP"
    "HP"
    "2020"
    "*"
			  SF-IMAGE    "theImage"		0
			  SF-IMAGE	  "neuesBild"		0
              ;SF-VALUE      "Bubble Width (px)" "200"
              ;SF-VALUE      "Bubble Height (px)" "200"
              ;SF-TOGGLE		"iWarp manually (For much better results), it will make the iWarp window pop" FALSE
              SF-ADJUSTMENT "Random Seed"	0         ;'(0 0 429496729 1 10 1 1)  ;for some reason i can't fet the max value of the randpm seed to it's true max of 4294967295 like in gimp 2.2. please fix it if you can.
              SF-ADJUSTMENT "Torbulence"         '(2 0.1 7 0.1 1 1 1)
              SF-ADJUSTMENT "Blur Factor"         '(8 0 50 0.1 1 1 1)
              SF-ADJUSTMENT "HighLight Rotation"         '(0 -180 180 0.1 1 1 1)
              ;SF-TOGGLE "Merge all layers when done" FALSE
)

(script-fu-menu-register "Call_script-fu-soap" "<Image>/_xTools/")

(define (Call_script-fu-soap theImage neuesBild seed turb blur rotation)

	(let*
			(
			(width 200)
			(height 200)
			(manual FALSE)
			;(seed '(0 0 429496729 1 10 1 1) )
			;(turb '(2 0.1 7 0.1 1 1 1))
			;(blur '(8 0 50 0.1 1 1 1))
			;(rotation '(0 -180 180 0.1 1 1 1))
			(merge FALSE)
			(actLayer (gimp-image-get-active-layer theImage))
			(bubble1 0)
			(actLayerneu (gimp-image-get-active-layer neuesBild))

			)

			(gimp-edit-copy (car actLayer)) ;actLayer von aktuellem Bild in Zwischenablage
			(set! bubble1 (gimp-edit-paste (car actLayerneu) 0)) ;Zwischenablage einfügen über aktLayerneu
			(gimp-floating-sel-to-layer (car bubble1)) ;schwebende Ebene zur neuen machen

			(plug-in-plasma 1 neuesBild bubble1 seed turb)


			;(script-fu-soap1 width height manual seed turb blur rotation merge)

	)
)
