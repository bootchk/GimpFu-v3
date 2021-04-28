
(define (210-script-fu-testGegl image drawable)
   (let*
       (
          (a '( 1.0 ))

       )
       (print a)
    )

  (gimp-drawable-apply-operation-by-name drawable "gegl:median-blur" 1 '("radius") 1 #( 1e0 ) )
)


(script-fu-register
   "210-script-fu-testGegl"                        ;func name
   "Test Gegl ops in scriptfu"                 ;menu label
   "Test gegl op"                              ;description
   "lkk"                       ;author
   ""                          ;copyright notice
   "Jan. 2021"                 ;date created
   "*"                     ;image type that the script works on
   SF-IMAGE "SF-IMAGE" 0
   SF-DRAWABLE "SF-DRAWABLE" 0
)
(script-fu-menu-register "210-script-fu-testGegl" "<Image>/Test")
