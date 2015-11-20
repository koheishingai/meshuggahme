#!/usr/bin/env python

import os
import json
import redis
import time
from muxer import Muxer, get_ytid_from_url
from analyzer.meshuggahme import load_models, meshuggahme, improve_normal

output_dir = os.environ['MESHUGGAHME_OUTPUT_PATH']

redis = redis.StrictRedis(host='localhost', port=6379, db=0)

def muxer_worker():
    global redis
    global onset_dicts, onset_dir, X, Y, Z

    while True:
        try:
            yt_url = redis.lpop('yturls')
            if not yt_url:
                time.sleep(10)
                next
            m = Muxer(yt_url=yt_url)
            m.download_video()
            with open(
                '{output_dir}/{ytid}.status.json'.format(output_dir=output_dir, ytid=m.ytid), 'w'
            ) as f:
                f.write('{"status": "processing", "stage": 1}')
            m.demux()
            with open(
                '{output_dir}/{ytid}.status.json'.format(output_dir=output_dir, ytid=m.ytid), 'w'
            ) as f:
                f.write('{"status": "processing", "stage": 2}')
            m.convert_to_wav()
            with open(
                '{output_dir}/{ytid}.status.json'.format(output_dir=output_dir, ytid=m.ytid), 'w'
            ) as f:
                f.write('{"status": "processing", "stage": 3}')
            # XXX: Call meshuggahfier here, and use its output in place of m.get_audio_file() 
            meshuggahfied_file = '{output_path}/{ytid}mm.wav'.format(
                output_path=m.output_dir, ytid=m.ytid
            )
            meshuggahme(
                m.get_audio_file(), 
                X, improve_func=improve_normal,
                onset_dicts=onset_dicts, onset_dir=onset_dir,
                metric='correlation', output_file=meshuggahfied_file,
                original_w=6.5
            )
            with open(
                '{output_dir}/{ytid}.status.json'.format(output_dir=output_dir, ytid=m.ytid), 'w'
            ) as f:
                f.write('{"status": "processing", "stage": 4}')
            meshuggahfied_file = m.compress_wav(meshuggahfied_file)
            with open(
                '{output_dir}/{ytid}.status.json'.format(output_dir=output_dir, ytid=m.ytid), 'w'
            ) as f:
                f.write('{"status": "processing", "stage": 5}')
            m.remux(meshugahfied_file).split('/')[-1]
            with open(
                '{output_dir}/{ytid}.status.json'.format(output_dir=output_dir, ytid=m.ytid), 'w'
            ) as f:
                f.write('{"status": "complete"}')
        except Exception as e:
            print repr(e)

if __name__ = "__main__":
    muxer_worker()