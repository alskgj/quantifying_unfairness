from json import load
from config import OUTPUT_DIR, HAR_DIR
from os.path import join

import pygal
import logging

# svg to pdf with:
# cairosvg vimeo_e2_combinedplot.svg -o out.pdf


from vimeo_har import VimeoHar
from postprocessor import YoutubeHar

logger = logging.getLogger(__name__)


def plot_vimeo_quality_vs_time(name):
    """ Takes the name of an experiment (e.g. vimeo_e2) and outputs 3 plots:
    combined, metadata only, har file only.
    """
    metadata_path = join(OUTPUT_DIR, name+'_metadata.json')
    har_path = join(HAR_DIR, name+'_har.json')

    metaplot(name, metadata_path)
    harplot(name, har_path)
    combined_plot(name, metadata_path, har_path)


def plot_youtube_quality_vs_time(name):
    """Takes the name of an experiment (e.g. youtube_e1) and outputs 3 plots:
    combined, metadata only, har file only."""
    metadata_path = join(HAR_DIR, name+'_metadata.json')
    har_path = join(HAR_DIR, name+'_har.json')

    metaplot(name, metadata_path)
    harplot(name, har_path)


def plot_combined_mb_vs_time(name):
    vimeo_data = VimeoHar(join(HAR_DIR, 'vimeo_'+name+'_har.json')).plot_mb_time()
    youtube_data = YoutubeHar(join(HAR_DIR, 'youtube_'+name+'_har.json')).plot_yt_time()

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True, stroke_style={'width': 5})

    line_chart.add('Vimeo', vimeo_data)
    line_chart.add('Youtube', youtube_data)

    path = join(OUTPUT_DIR, 'mb_'+name)
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')


def plot_combined_bandwidth_vs_time(name, n=3):
    vimeohar = VimeoHar(join(HAR_DIR, 'vimeo_'+name+'_har.json'))
    youtubehar = YoutubeHar(join(HAR_DIR, 'youtube_'+name+'_har.json'))
    vimeo_data, vimeo_start = vimeohar.plot_bandwidth_time(n), vimeohar.starttime()
    youtube_data, youtube_start = youtubehar.plot_bandwidth_time(n), youtubehar.starttime()

    # shift data to the right if playback wasn't started at the same time
    if youtube_start > vimeo_start:
        youtube_data = [(time+(youtube_start-vimeo_start).total_seconds(), br) for time, br in youtube_data]
    else:
        vimeo_data = [(time+(vimeo_start-youtube_start).total_seconds(), br) for time, br in vimeo_data]

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True, stroke_style={'width': 5},
                          x_title='Time (sec)', y_title='Bandwidth (Mbit/s)',)

    line_chart.add('Vimeo', vimeo_data)
    line_chart.add('Youtube', youtube_data)

    path = join(OUTPUT_DIR, 'bandwidth_'+name)
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')


def plot_combined_bandwidth_vs_time_add_youtube_rbuf(name, n=3):
    vimeohar = VimeoHar(join(HAR_DIR, 'vimeo_'+name+'_har.json'))
    youtubehar = YoutubeHar(join(HAR_DIR, 'youtube_'+name+'_har.json'))
    vimeo_data, vimeo_start = vimeohar.plot_bandwidth_time(n), vimeohar.starttime()
    youtube_data, youtube_start = youtubehar.plot_bandwidth_time(n), youtubehar.starttime()
    youtube_rbuf = youtubehar.plot_rbuf_time()

    # shift data to the right if playback wasn't started at the same time
    if youtube_start > vimeo_start:
        youtube_data = [(time+(youtube_start-vimeo_start).total_seconds(), br) for time, br in youtube_data]
        youtube_rbuf = [(time+(youtube_start-vimeo_start).total_seconds(), rbuf) for time, rbuf in youtube_rbuf]
    else:
        vimeo_data = [(time+(vimeo_start-youtube_start).total_seconds(), br) for time, br in vimeo_data]

    last_timestamp = max(vimeo_data[-1][0], youtube_data[-1][0])
    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True,
                          stroke_style={'width': 5}, range=(0, 5), secondary_range=(0, 50),
                          xrange=(0, last_timestamp+10),
                          x_title='Time (sec)', y_title='Bandwidth (Mbit/s)',
                          secondary_title='Buffer (Mbit)')
    print(youtube_rbuf)
    print(last_timestamp)


    line_chart.add('Vimeo', vimeo_data)
    line_chart.add('Youtube', youtube_data)
    line_chart.add('Youtube Buffer', youtube_rbuf, secondary=True, colour='black')

    path = join(OUTPUT_DIR, 'bandwidth_ytrbuf_'+name)
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')


def metaplot(name, path):
    logger.info(f'Loaded file {path} for plotting')

    metadata = load(open(path))

    line_chart = pygal.XY()
    line_chart.title = f'Metadata {name}'

    line_chart.y_labels = [0, 240, 360, 480, 720, 1080]
    line_chart.x_labels = (int(e['time']) for e in metadata)

    x_points = meta_to_pyglot(metadata)
    line_chart.add('Metadata', x_points)  # Add some values

    path = join(OUTPUT_DIR, name+'_metaplot')
    line_chart.render_to_file(path+'.svg')
    line_chart.render_to_png(path+'.png')
    logger.info(f'Created plot at: {path}.png')

    line_chart.render_in_browser()


def meta_to_pyglot(data):
    """ Converts the metadata format to something plottable
    """
    # generate missing points
    duration = int(data[-1]['time'])
    x_points = []
    y = 0

    for i in range(0, duration+1):
        match = [e for e in data if int(e['time']) == i]
        # on a match we append the last point and the new point
        if match:
            match = match[0]['quality'][1]
            x_points.append((i, y))
            x_points.append((i, match))
            y = match

        else:
            x_points.append(None)
    return x_points


def harplot(name, path):
    if 'vimeo' in name.lower():
        data = VimeoHar(path).plot_time_quality()
    elif 'youtube' in name.lower():
        data = YoutubeHar(path).plot_time_quality()

    else:
        logger.error(f'harploter didn\'t recognize name {name} and does not know this format')
        return

    line_chart = pygal.XY()
    line_chart.title = f'Har {name}'

    line_chart.y_labels = [0, 240, 360, 480, 720, 1080]
    # change_points = [point[0] for point in data if point[1]] + [data[-1][0]]
    # line_chart.x_labels = change_points

    line_chart.add('Hardata', data)  # Add some values

    path = join(OUTPUT_DIR, name + '_harplot')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png')
    logger.info(f'Created plot at: {path}.png')


def combined_plot(name, metapath, harpath):
    if 'vimeo' in name.lower():
        hardata = VimeoHar(harpath).plot_time_quality()
    else:
        logger.error(f'harploter didn\'t recognize name {name} and does not know this format')
        return

    metadata = load(open(metapath))

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True, stroke_style={'width': 5})
    line_chart.y_labels = [0, 240, 360, 480, 720, 1080]

    line_chart.add('javascript api', meta_to_pyglot(metadata))  # Add some values
    line_chart.add('request headers', hardata)                    # Add some values

    path = join(OUTPUT_DIR, name + '_combinedplot')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')


if __name__ == '__main__':
    # plot_vimeo_quality_vs_time('vimeo_e2')
    NAME = 'newcomers_1'
    plot_combined_bandwidth_vs_time_add_youtube_rbuf(NAME, n=15)
    plot_combined_bandwidth_vs_time(NAME, n=15)
