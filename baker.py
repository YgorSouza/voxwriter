import time

import bpy


class Baker:
    def __init__(self, obj, width, height):
        self.__original_engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = 'CYCLES'
        self.__obj = obj
        image_name = obj.name + '_BakedTexture'
        self.__img = bpy.data.images.new(image_name, width, height)
        for mat in filter(None, self.__obj.data.materials):
            nodes = mat.node_tree.nodes
            texture_node = nodes.new('ShaderNodeTexImage')
            texture_node.name = 'voxwriter_bake_node'
            texture_node.select = True
            nodes.active = texture_node
            texture_node.image = self.__img
        self.__cleanup_pending = True

    def cleanup(self):
        if not self.__cleanup_pending:
            return
        self.__cleanup_pending = False
        bpy.context.scene.render.engine = self.__original_engine
        for mat in filter(None, self.__obj.data.materials):
            for n in mat.node_tree.nodes:
                if n.name == 'voxwriter_bake_node':
                    mat.node_tree.nodes.remove(n)
        # bpy.data.images.remove(self.__img)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def bake(self):
        bpy.context.view_layer.objects.active = self.__obj
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'},
                            save_mode='EXTERNAL')
        return self.__img


if __name__ == "__main__":
    import os
    from pathlib import Path
    home = str(Path.home())
    out_file_name = f"baked_texture_{time.strftime('%Y%m%d_%H%M%S')}.png"
    out_path = os.path.join(home, out_file_name)
    obj = bpy.context.active_object
    with Baker(obj, 512, 512) as baker:
        texture = baker.bake()
        print(len(texture.pixels))
        texture.save_render(filepath=out_path)
