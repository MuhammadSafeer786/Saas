import os
import cv2
import io
import numpy as np
import torch
from flask import Flask, request, jsonify, send_file
from gfpgan import GFPGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

app = Flask(__name__)

def setup_restorer():
    # Set default parameters
    version = '1.3'
    upscale = 2
    bg_upsampler_type = 'realesrgan'
    bg_tile = 400
    weight = 0.5

    # Set up background upsampler
    if bg_upsampler_type == 'realesrgan':
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
        bg_upsampler = RealESRGANer(
            scale=2,
            model_path='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth',
            model=model,
            tile=bg_tile,
            tile_pad=10,
            pre_pad=0,
            half=False)  # set False in CPU mode
    else:
        bg_upsampler = None

    # Set up GFPGAN restorer
    model_map = {
        '1': ('original', 1, 'GFPGANv1', 'https://github.com/TencentARC/GFPGAN/releases/download/v0.1.0/GFPGANv1.pth'),
        '1.2': ('clean', 2, 'GFPGANCleanv1-NoCE-C2', 'https://github.com/TencentARC/GFPGAN/releases/download/v0.2.0/GFPGANCleanv1-NoCE-C2.pth'),
        '1.3': ('clean', 2, 'GFPGANv1.3', 'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth'),
        '1.4': ('clean', 2, 'GFPGANv1.4', 'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth'),
        'RestoreFormer': ('RestoreFormer', 2, 'RestoreFormer', 'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/RestoreFormer.pth')
    }

    arch, channel_multiplier, model_name, url = model_map[version]

    # Determine model paths
    model_path = os.path.join('experiments/pretrained_models', model_name + '.pth')
    # if not os.path.isfile(model_path):
    #     model_path = os.path.join('gfpgan/weights', model_name + '.pth')
    if not os.path.isfile(model_path):
        model_path = url

    restorer = GFPGANer(
        model_path=model_path,
        upscale=upscale,
        arch=arch,
        channel_multiplier=channel_multiplier,
        bg_upsampler=bg_upsampler)

    return restorer

@app.route('/enhance', methods=['POST'])
def enhance_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    input_img = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)

    if input_img is None:
        return jsonify({'error': 'Invalid image'}), 500

    try:
        restorer = setup_restorer()
        cropped_faces, restored_faces, restored_img = restorer.enhance(
            input_img,
            has_aligned=False,
            only_center_face=False,
            paste_back=True,
            weight=0.5)

        if restored_img is None:
            return jsonify({"error": "Restoration failed"}), 500

        _, buffer = cv2.imencode('.png', restored_img)
        response_image = buffer.tobytes()

        return send_file(
            io.BytesIO(response_image),
            mimetype='image/png',
            as_attachment=True,
            download_name='restored.png'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
