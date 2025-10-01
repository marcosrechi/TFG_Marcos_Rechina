**COSAS TFG**

Cintia barajas (secretaria de la escuela, profesora TMM)
Elena Cerro (Jefa de Estudios)
Perpignan (Profesor de TFG de Junki)


Datos Importantes Necesarios
Aforo de las aulas
Matriculados de las asignaturas (gente que va al examen)

Aplicación Gauss
Metadatos de alumnos que se matriculan, presentan, aprueban, etc.


No se si asignación de aulas puras (que las restricciones solo se hagan por eso)
O que tmbn haya restricciones teniendo en cuenta la dificultad de las asignaturas (tasa de aprobados etc)


herramienta de Google or tools te inventas las restricciones las pones como puedas y creas una variable que sea una asignación

X[aula][asignatura][horario]
por ejemplo


y cuando coinciden todas (aula i en asignatura j en el horario k) entonces X[i][j][k] = 1
Se le ha asignado
Y con add añades las diferentes restricciones

Algo asi