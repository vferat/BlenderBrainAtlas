import nibabel as nib
import numpy as np
import bpy
import bmesh
import time

lut = r'C:\Users\Victor\Desktop\Python\lut.txt'
mri = r'C:\Users\Victor\mne_data\MNE-fsaverage-data\fsaverage\mri\aparc+aseg.mgz'
# open lut
dtype = [('id', '<i8'), ('name', 'U47'),
        ('R', '<i8'), ('G', '<i8'), ('B', '<i8'), ('A', '<i8')]
data_lut = np.genfromtxt(lut, dtype=dtype)
# open mri
mri_img = nib.load(mri)
mri_data = mri_img.get_fdata()
# Get target indices
target_indices = np.unique(mri_data)


def draw_face(voxel_pos, where, dim=1):
    if where == "x-" :
        v1 = [voxel_pos[0] - dim/2, voxel_pos[1] + dim/2, voxel_pos[2] + dim/2]
        v2 = [voxel_pos[0] - dim/2, voxel_pos[1] + dim/2, voxel_pos[2] - dim/2]
        v3 = [voxel_pos[0] - dim/2, voxel_pos[1] - dim/2, voxel_pos[2] - dim/2]
        v4 = [voxel_pos[0] - dim/2, voxel_pos[1] - dim/2, voxel_pos[2] + dim/2]
    elif where == "x+":
        v1 = [voxel_pos[0] + dim/2, voxel_pos[1] + dim/2, voxel_pos[2] + dim/2]
        v2 = [voxel_pos[0] + dim/2, voxel_pos[1] + dim/2, voxel_pos[2] - dim/2]
        v3 = [voxel_pos[0] + dim/2, voxel_pos[1] - dim/2, voxel_pos[2] - dim/2]
        v4 = [voxel_pos[0] + dim/2, voxel_pos[1] - dim/2, voxel_pos[2] + dim/2]
    elif where == "y-":
        v1 = [voxel_pos[0] + dim/2, voxel_pos[1] - dim/2, voxel_pos[2] + dim/2]
        v2 = [voxel_pos[0] + dim/2, voxel_pos[1] - dim/2, voxel_pos[2] - dim/2]
        v3 = [voxel_pos[0] - dim/2, voxel_pos[1] - dim/2, voxel_pos[2] - dim/2]
        v4 = [voxel_pos[0] - dim/2, voxel_pos[1] - dim/2, voxel_pos[2] + dim/2]
    elif where == "y+":
        v1 = [voxel_pos[0] + dim/2, voxel_pos[1] + dim/2, voxel_pos[2] + dim/2]
        v2 = [voxel_pos[0] + dim/2, voxel_pos[1] + dim/2, voxel_pos[2] - dim/2]
        v3 = [voxel_pos[0] - dim/2, voxel_pos[1] + dim/2, voxel_pos[2] - dim/2]
        v4 = [voxel_pos[0] - dim/2, voxel_pos[1] + dim/2, voxel_pos[2] + dim/2]
    elif where == "z-":
        v1 = [voxel_pos[0] + dim/2, voxel_pos[1] + dim/2, voxel_pos[2] - dim/2]
        v2 = [voxel_pos[0] + dim/2, voxel_pos[1] - dim/2, voxel_pos[2] - dim/2]
        v3 = [voxel_pos[0] - dim/2, voxel_pos[1] - dim/2, voxel_pos[2] - dim/2]
        v4 = [voxel_pos[0] - dim/2, voxel_pos[1] + dim/2, voxel_pos[2] - dim/2]
    elif where == "z+":
        v1 = [voxel_pos[0] + dim/2, voxel_pos[1] + dim/2, voxel_pos[2] + dim/2]
        v2 = [voxel_pos[0] + dim/2, voxel_pos[1] - dim/2, voxel_pos[2] + dim/2]
        v3 = [voxel_pos[0] - dim/2, voxel_pos[1] - dim/2, voxel_pos[2] + dim/2]
        v4 = [voxel_pos[0] - dim/2, voxel_pos[1] + dim/2, voxel_pos[2] + dim/2]
    return([v1, v2, v3, v4])


col = bpy.data.collections.get("Collection")
# for each region
for c,i in enumerate(target_indices):
    if i  >= 1:
        lut_ind = np.where(data_lut['id']==i)[0][0]
        b_name = data_lut['name'][lut_ind]
        R = data_lut['R'][lut_ind] / 255.
        G = data_lut['G'][lut_ind] / 255.
        B = data_lut['B'][lut_ind] / 255.
        A = data_lut['A'][lut_ind] / 255.
        print(b_name, R, G ,B)
        mesh = bpy.data.meshes.new(b_name)  # add the new mesh
        obj = bpy.data.objects.new(mesh.name, mesh)
        
        mat = bpy.data.materials.new(name=b_name)
        mat.diffuse_color = (R,G,B,1)
        obj.data.materials.append(mat)
        
        #obj.show_name = True
        col.objects.link(obj)
        me = obj.data

        faces = list()
        mask = np.where(mri_data == i, 1, 0)
        pos = np.argwhere(mask==1)
        for p in pos:
            x = p[0]
            y = p[1]
            z = p[2]
            if mask[x+1,y,z]==0:
                faces.append(draw_face(p, "x+"))
            if mask[x-1,y,z]==0:
                faces.append(draw_face(p, "x-"))
            if mask[x,y+1,z]==0:
                faces.append(draw_face(p, "y+"))
            if mask[x,y-1,z]==0:
                faces.append(draw_face(p, "y-"))
            if mask[x,y,z+1]==0:
                faces.append(draw_face(p, "z+"))
            if mask[x,y,z-1]==0:
                faces.append(draw_face(p, "z-"))
                     
        all_faces = np.array(faces)
        uniques_vertices = np.unique(np.concatenate(all_faces), axis=0)
            
        FACES = np.zeros(all_faces.shape[:-1],dtype=int)
        for p,vert in enumerate(uniques_vertices):
            mask = np.where((all_faces == vert).all(axis=-1))
            FACES[mask[0],mask[1]] = p

        me.from_pydata(uniques_vertices, edges=[], faces=FACES.tolist())
        me.update()