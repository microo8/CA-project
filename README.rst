==========
CA project
==========

*autor:* Bc. Vladimir Magyar

Project theme C03 - Inverse Kinematics:
---------------------------------------

- Scene: 2d line-segment skeleton of figure (min 15 bones)
- Implement 2d skeleton creation
        - User can create new bone by selecting parent bone (click on it) and clicking anywhere to define end of bone
        - Bones can have more child bones
        - Each bone has its position, rotation angle and length (end point can be calculated)
        - User can select starting and ending bone of the IK sequence
- Implement forward kinematics
        - Select bone by clicking, change rotation angle by dragging
        - Child bones must be transformed correctly (can use transformation 3x3 matrices - they handle both rotation and translation)
- Implement inverse kinematics (relaxation by gradient calculation)
        - User can move end bone - IK solves bones in the IK sequence
