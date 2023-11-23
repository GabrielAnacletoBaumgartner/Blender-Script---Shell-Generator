import bpy
import os
import numpy as np
import bmesh

# Options:

ClearConsole = True
debug0 = False # Debug message for the checks step.
debug1 = False # Debug message for the shell clones.
debug2 = False
debug3 = False
ShellCount = 16 # Ammount of shells (Must be more than 0).
ShellDistance = 0.01 # Distance of shells (must be more than 0).
ShellMode = "Simple" # Type of shell (Must be "Simple" or "Complex").
IsShellInternal = False #Set this to True if you want your shell to be internal.
ApplyModifier = True # Automatically applies the modifier if set to True.
RemoveBaseVertexes = True # If set to true, automatically removes the vertices in the same position of the Base object from the shell objects.
SelectLinkedFix = True # EXPERIMENTAL THING. For now leave it as it is. I've done this way for two reasons: Performance and Blender being unable to find the matching vertexes with too many shells (at least with the method i used).

#Variables:

Check = True

if (ClearConsole == True): # As the name suggests it clears the console if ClearConsole is active.
    os.system('cls')

# Checks:

if (ShellCount <= 0):
    if (debug0 == True):
        print("ShellCount is equal or less than zero.") # Verify if the ammount of shells is valid (more than zero).
    Check = False

if (ShellDistance <= 0):
    if (debug0 == True):
        print("ShellDistance is equal or less than zero.") # Verifiy if the distance between shells is valid.
    Check = False

if (ShellMode != "Simple")and(ShellMode != "Complex"): # Verify if Shell Mode is valid.
    if (debug0 == True):
        print("ShellMode is invalid")
    Check = False
    
base_shell_object = bpy.context.active_object
if (base_shell_object == None)and(base_shell_object.type == "MESH"): # Verify if there is a selected object and if the selected object type equals MESH.
    if (debug0 == True):
        print("Invalid object selection")
    Check = False

#Code starts here:

if (Check == True): # Execute the code if everything went well during the checks step.

    if (debug0 == True):
        print("Everything is ok.")

    for i in range (0,ShellCount):
        shell_object = base_shell_object.copy()
        shell_object.data = base_shell_object.data.copy()
        shell_object.animation_data_clear()
        bpy.context.collection.objects.link(shell_object)
        shell_mod = shell_object.modifiers.new("Shell", "SOLIDIFY")
        shell_mod.use_rim = False
        if (IsShellInternal == False):
            shell_mod.thickness = (-1*((i+1)*ShellDistance))
        if (IsShellInternal == True):
            shell_mod.thickness = ((i+1)*ShellDistance)
        if (ShellMode == "Simple"):
            shell_object.modifiers["Shell"].solidify_mode = 'EXTRUDE'
        if (ShellMode == "Complex"):
            shell_object.modifiers["Shell"].solidify_mode = 'NON_MANIFOLD'
        if (ApplyModifier == True):
            bpy.context.view_layer.objects.active = shell_object
            bpy.ops.object.modifier_apply(modifier="Shell")\
            
        if (RemoveBaseVertexes == True):

            for base_vertex in base_shell_object.data.vertices:
                if (debug1 == True):
                    print("Shell Base Object:", base_shell_object)
                    print(base_vertex)
                co_base = base_shell_object.matrix_world @ base_vertex.co
                if (debug2 == True):
                    print("")
                    print("Searching for these:")
                    print("Coordinates from base:", co_base)
                    print("")
                for shell_vertex in shell_object.data.vertices: # Checks each vertex from Shell Object
                    co_shell = shell_object.matrix_world @ shell_vertex.co # Gets coordinates from each vertex
                    if (debug3 == True):
                        print("Shell Object:", shell_object, ". Coordinates:", co_shell)
                    if (co_base == co_shell): # If its coordinates matches the coordinates of the base object
                        MatchIndex = shell_vertex.index
                        if (debug3 == True):
                            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                            print(" ---------- MATCH FOUND ----------")
                            print("Matching vertex is:", shell_vertex)
                            print("It's index number is:", MatchIndex)
                            print("")
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_mode(type="VERT")
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='OBJECT')
                        shell_object.data.vertices[MatchIndex].select = True # Select the vertex
                        bpy.ops.object.mode_set(mode='EDIT')                        
                        if (SelectLinkedFix == True):
                            bpy.ops.mesh.select_linked(delimit=set())
                        bpy.ops.mesh.delete(type='VERT') # And delete it.
                        bpy.ops.object.mode_set(mode='OBJECT')
                
else: # Ends the script if something went wrong during the checks step.
    if(debug0 == True):
        print("ERROR. Something went wrong.")
