from json import load
from config import OUTPUT_DIR, HAR_DIR
from os.path import join
import os

import pygal
import logging

# svg to pdf with:
# cairosvg vimeo_e2_combinedplot.svg -o out.pdf

from postprocessor.har import VimeoHar

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
    youtube_data = YoutubeHar(join(HAR_DIR, 'youtube_'+name+'_har.json')).plot_mb_time()

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True,
                          # stroke_style={'width': 5},
                          x_title='Time (sec)', y_title='MB downloaded')

    line_chart.add('Vimeo', vimeo_data)
    line_chart.add('Youtube', youtube_data)

    path = join(OUTPUT_DIR, name + '_mb')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')


def plot_combined_bandwidth_vs_time(name, n=3, annotate=False):
    vimeohar = VimeoHar(join(HAR_DIR, 'vimeo_'+name+'_har.json'))
    youtubehar = YoutubeHar(join(HAR_DIR, 'youtube_'+name+'_har.json'))
    vimeo_data, vimeo_start = vimeohar.plot_bandwidth_time(n), vimeohar.starttime()
    youtube_data, youtube_start = youtubehar.plot_bandwidth_time(n), youtubehar.starttime()

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True,
                          x_title='Time (sec)', y_title='Bandwidth (Mbit/s)',)

    # shift data to the right if playback wasn't started at the same time
    max_bw = max(youtube_data+vimeo_data, key=lambda e: e[1])[1]
    if youtube_start > vimeo_start:
        diff = (youtube_start-vimeo_start).total_seconds()
        youtube_data = [(time+diff, br) for time, br in youtube_data]
        if annotate:
            line_chart.add('Youtube starts playing', [(diff, 0), (diff, max_bw)])
    else:
        diff = (youtube_start - vimeo_start).total_seconds()
        vimeo_data = [(time+diff, br) for time, br in vimeo_data]
        if annotate:
            line_chart.add('Vimeo starts playing', [(diff, 0), (diff, max_bw)])

    line_chart.add('Vimeo', vimeo_data)
    line_chart.add('Youtube', youtube_data)

    path = join(OUTPUT_DIR, name + '_bandwidth')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')


def plot_combined_bandwidth_vs_time_add_youtube_rbuf(name, n=3, annotate=False):
    vimeohar = VimeoHar(join(HAR_DIR, 'vimeo_'+name+'_har.json'))
    youtubehar = YoutubeHar(join(HAR_DIR, 'youtube_'+name+'_har.json'))
    vimeo_data, vimeo_start = vimeohar.plot_bandwidth_time(n), vimeohar.starttime()
    youtube_data, youtube_start = youtubehar.plot_bandwidth_time(n), youtubehar.starttime()
    youtube_rbuf = youtubehar.plot_rbuf_time()



    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True,
                          # stroke_style={'width': 5},
                          range=(0, 5), secondary_range=(0, 50),
                          x_title='Time (sec)', y_title='Bandwidth (Mbit/s)',
                          secondary_title='Buffer (Mbit)')

    # shift data to the right if playback wasn't started at the same time
    max_bw = max(youtube_data + vimeo_data, key=lambda e: e[1])[1]
    if youtube_start > vimeo_start:
        diff = (youtube_start - vimeo_start).total_seconds()
        youtube_data = [(time+diff, br) for time, br in youtube_data]
        youtube_rbuf = [(time+diff, rbuf) for time, rbuf in youtube_rbuf]
        if annotate:
            line_chart.add('Youtube starts playing', [(diff, 0), (diff, max_bw)])
    else:
        diff = (youtube_start - vimeo_start).total_seconds()
        vimeo_data = [(time+diff, br) for time, br in vimeo_data]
        if annotate:
            line_chart.add('Vimeo starts playing', [(diff, 0), (diff, max_bw)])

    last_timestamp = max(vimeo_data[-1][0], youtube_data[-1][0])
    line_chart.x_range = (0, last_timestamp+10)

    print(youtube_rbuf)
    print(last_timestamp)


    line_chart.add('Vimeo', vimeo_data)
    line_chart.add('Youtube', youtube_data)
    line_chart.add('Youtube Buffer', youtube_rbuf, secondary=True, colour='black')

    path = join(OUTPUT_DIR, name + '_bandwidth_ytrbuf')
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
    # accepts metadata or path to metadata
    if isinstance(data, str):
        data = load(open(data))

    # generate missing points
    duration = int(data[-1]['time'])
    x_points = []
    y = 0

    for i in range(0, duration+1):
        match = [e for e in data if int(e['time']) == i]
        # on a match we append the last point and the new point
        if match:
            match = match[0]

            if not match['quality'] or match['rebuffering']:
                quality = 0
            else:
                quality = match['quality'][1]

            x_points.append((i, y))
            x_points.append((i, quality))
            y = quality
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


def plot_combined_quality(NAME):
    vimeopath = join(HAR_DIR, 'vimeo_'+NAME+'_metadata.json')
    youtubepath = join(HAR_DIR, 'youtube_'+NAME+'_metadata.json')
    vimeo_data, youtube_data = meta_to_pyglot(vimeopath), meta_to_pyglot(youtubepath)

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True,
                          #stroke_style={'width': 5},
                          range=(0, 5),
                          x_title='Time (sec)', y_title='Resolution (0 is rebuffering)',
                          y_labels=[0, 240, 360, 480, 720, 1080])
    print(youtube_data)
    line_chart.add('Vimeo playback quality', vimeo_data)
    line_chart.add('Youtube playback quality', youtube_data)

    path = join(OUTPUT_DIR, NAME + '_quality')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')


def _shift(start_1, start_2, data_2, data_1, annotate, line_chart, name_1='Vimeo', name_2='Youtube'):
    # account for not starting at the same time
    if abs((start_1 - start_2).total_seconds()) > 1:
        max_bw = max(data_2 + data_1, key=lambda e: e[1] if e else 0)[1]
        # vimeo_was started earlier
        if start_2 > start_1:
            diff = (start_2 - start_1).total_seconds()
            data_2 = [(time + diff, br) for time, br in data_2]
            if annotate:
                line_chart.add(f'{name_2} starts playing', [(diff, 0), (diff, max_bw)])
        # youtube was started earlier
        else:
            diff = (start_1 - start_2).total_seconds()
            data_1 = [(time + diff, br) for time, br in data_1]
            if annotate:
                line_chart.add(f'{name_1} starts playing', [(diff, 0), (diff, max_bw)])
    return data_1, data_2


def plot_combined(NAME, primary, secondary=None, annotated=False, annotate=True, omit_secondary_vimeo=False):
    """All the plotting needed. If you have a vimeo and a youtube video, this is the function you want to use

    omit_secondary_vimeo: don't show vimeos buffer. only ussed if primary or secondary arg is 'buffer'
    """

    # sanity check
    args = ['mb', 'bandwidth', 'quality', 'buffer', 'interpolated']
    if primary not in args:
        print(f'Supplied unknown argument {primary}. Expected one of {args}')
        raise NotImplementedError
    if secondary and secondary not in args:
        print(f'Supplied unknown argument {secondary}. Expected one of {args}')
        raise NotImplementedError

    vimeo_har = VimeoHar(join(HAR_DIR, 'vimeo_' + NAME + '_har.json'))
    youtube_har = YoutubeHar(join(HAR_DIR, 'youtube_' + NAME + '_har.json'))
    vimeo_meta = join(HAR_DIR, 'vimeo_' + NAME + '_metadata.json')
    youtube_meta = join(HAR_DIR, 'youtube_' + NAME + '_metadata.json')

    vimeo_start, youtube_start = vimeo_har.starttime(), youtube_har.starttime()

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True,
                          x_title='Time (sec)',
                          dots_size=0,
                          stroke_style={'width': 3})
    if primary in ['bandwidth', 'interpolated'] and secondary == 'buffer':
        line_chart.secondary_range = (0, 50)

    # for each option we load the data and generate the legend
    if primary == 'mb':
        vimeo_data = vimeo_har.plot_mb_time()
        youtube_data = youtube_har.plot_mb_time()
        line_chart.y_title = 'MB downloaded'
        statistic = 'Data downloaded'
    elif primary == 'bandwidth':
        vimeo_data = vimeo_har.plot_bandwidth_time(15)
        youtube_data = youtube_har.plot_bandwidth_time(15)
        line_chart.y_title = 'Bandwidth (Mbit/s)'
        statistic = 'Bandwidth'
        line_chart.range = (0, 5)
    elif primary == 'quality':
        vimeo_data = meta_to_pyglot(vimeo_meta)
        youtube_data = meta_to_pyglot(youtube_meta)
        line_chart.y_title = 'Resolution (0 is rebuffering)'
        statistic = 'playback quality'
        line_chart.y_labels = [0, 240, 360, 480, 540, 720, 1080]
    elif primary == 'buffer':
        vimeo_data = get_vimeo_buffer(NAME)
        youtube_data = youtube_har.plot_rbuf_time()
        line_chart.y_title = 'Buffer available (Seconds)'
        statistic = 'Buffer (Seconds)'
    elif primary == 'interpolated':
        vimeo_data = vimeo_har.plot_bandwidth_interpolated()
        youtube_data = youtube_har.plot_bandwidth_interpolated()
        line_chart.y_title = 'Bandwidth (Mbit/s)'
        statistic = 'Bandwidth'
        line_chart.range = (0, 5)
        line_chart.interpolate = 'cubic'


    else:
        raise NotImplementedError(f'Primary parameter {primary} not supported')

    vimeo_data, youtube_data = _shift(data_1=vimeo_data,
                                      data_2=youtube_data,
                                      start_1=vimeo_start,
                                      start_2=youtube_start,
                                      annotate=annotate,
                                      line_chart=line_chart)
    # add primary data
    # line_chart.add(f'Vimeo ({statistic})', vimeo_data)
    # line_chart.add(f'Youtube ({statistic})', youtube_data)
    line_chart.add(f'Vimeo', vimeo_data)
    line_chart.add(f'Youtube', youtube_data)

    # secondary
    # for each option we load the data and generate the legend
    if secondary == 'mb':
        vimeo_data = vimeo_har.plot_mb_time()
        youtube_data = youtube_har.plot_mb_time()
        statistic = 'Data downloaded'
    elif secondary == 'bandwidth':
        vimeo_data = vimeo_har.plot_bandwidth_time(15)
        youtube_data = youtube_har.plot_bandwidth_time(15)
        statistic = 'Bandwidth'
    elif secondary == 'quality':
        vimeo_data = meta_to_pyglot(vimeo_meta)
        youtube_data = meta_to_pyglot(youtube_meta)
        statistic = 'playback quality'
    elif secondary == 'buffer':
        vimeo_data = get_vimeo_buffer(NAME)
        youtube_data = youtube_har.plot_rbuf_time()
        statistic = 'Buffer (Seconds)'
        #line_chart.secondary_range = (0, 75)

    elif secondary:
        raise NotImplementedError(f'Secondary parameter {secondary} not supported')
    if secondary:
        vimeo_data, youtube_data = _shift(data_1=vimeo_data,
                                          data_2=youtube_data,
                                          start_1=vimeo_start,
                                          start_2=youtube_start,
                                          annotate=False,
                                          line_chart=line_chart)
        line_chart.add(f'Youtube {statistic}', youtube_data, secondary=True)
        if not omit_secondary_vimeo:
            line_chart.add(f'Vimeo {statistic}', vimeo_data, secondary=True)

    # plot everything
    folder = join(OUTPUT_DIR, NAME)
    if not os.path.exists(folder):
        os.mkdir(folder)
    if secondary:
        path = join(folder, f'{primary}_{secondary}')
    else:
        path = join(folder, f'{primary}')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')


def plot_2youtube(NAME, primary, secondary=None, annotated=False, annotate=True, name1 = None,
                  name2 = None):
    """All the plotting needed if you want to compare two youtube playbacks"""

    # sanity check
    args = ['mb', 'bandwidth', 'quality', 'buffer', 'interpolated']
    if primary not in args:
        print(f'Supplied unknown argument {primary}. Expected one of {args}')
        raise NotImplementedError
    if secondary and secondary not in args:
        print(f'Supplied unknown argument {secondary}. Expected one of {args}')
        raise NotImplementedError

    if name1:
        yt1_har = YoutubeHar(join(HAR_DIR, name1 + '_har.json'))
        yt1_meta = join(HAR_DIR, name1 + '_metadata.json')
    else:
        yt1_har = YoutubeHar(join(HAR_DIR, 'youtube_1_' + NAME + '_har.json'))
        yt1_meta = join(HAR_DIR, 'youtube_1_' + NAME + '_metadata.json')
    if name2:
        yt2_har = YoutubeHar(join(HAR_DIR, name2 + '_har.json'))
        yt2_meta = join(HAR_DIR, name2 + '_metadata.json')
    else:
        yt2_har = YoutubeHar(join(HAR_DIR, 'youtube_2_' + NAME + '_har.json'))
        yt2_meta = join(HAR_DIR, 'youtube_2_' + NAME + '_metadata.json')

    yt1_start, yt2_start = yt1_har.starttime(), yt2_har.starttime()

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True,
                          x_title='Time (sec)',
                          dots_size=0,
                          stroke_style={'width': 3})

    # for each option we load the data and generate the legend
    if primary == 'mb':
        yt1_data = yt1_har.plot_mb_time()
        yt2_data = yt2_har.plot_mb_time()
        line_chart.y_title = 'MB downloaded'
        statistic = 'Data downloaded'
    elif primary == 'bandwidth':
        yt1_data = yt1_har.plot_bandwidth_time(15)
        yt2_data = yt2_har.plot_bandwidth_time(15)
        line_chart.y_title = 'Bandwidth (Mbit/s)'
        statistic = 'Bandwidth'
        line_chart.range = (0, 5)
    elif primary == 'interpolated':
        yt1_data = yt1_har.plot_bandwidth_interpolated()
        yt2_data = yt2_har.plot_bandwidth_interpolated()
        line_chart.y_title = 'Bandwidth (Mbit/s)'
        statistic = 'Bandwidth (interpolated)'
        line_chart.range = (0, 5)
    elif primary == 'quality':
        yt1_data = meta_to_pyglot(yt1_meta)
        yt2_data = meta_to_pyglot(yt2_meta)
        #  yt1_data = [data for data in yt1_data if data[0] < 200]  # zoom to values < 200
        #  yt2_data = [data for data in yt2_data if data[0] < 200]  # zoom to values < 200

        line_chart.y_title = 'Resolution (0 is rebuffering)'
        statistic = 'playback quality'
        line_chart.y_labels = [0, 240, 360, 480, 540, 720, 1080]
    elif primary == 'buffer':
        yt1_data = yt1_har.plot_rbuf_time()
        yt2_data = yt2_har.plot_rbuf_time()
        line_chart.y_title = 'Buffer available (Seconds)'
        statistic = 'Buffer (Seconds)'
    else:
        raise NotImplementedError(f'Primary parameter {primary} not supported')

    yt1_data, yt2_data = _shift(data_1=yt1_data,
                                data_2=yt2_data,
                                start_1=yt1_start,
                                start_2=yt2_start,
                                annotate=annotate,
                                line_chart=line_chart,
                                name_1='Youtube 1',
                                name_2='Youtube 2')
    # add primary data
    line_chart.add(f'Youtube 1', yt1_data)
    line_chart.add(f'Youtube 2', yt2_data)

    # secondary
    # for each option we load the data and generate the legend
    if secondary == 'mb':
        yt1_data = yt1_har.plot_mb_time()
        yt2_data = yt2_har.plot_mb_time()
        statistic = 'Data downloaded'
    elif secondary == 'bandwidth':
        yt1_data = yt1_har.plot_bandwidth_time(15)
        yt2_data = yt2_har.plot_bandwidth_time(15)
        statistic = 'Bandwidth'
    elif secondary == 'quality':
        yt1_data = meta_to_pyglot(yt1_meta)
        yt2_data = meta_to_pyglot(yt2_meta)
        statistic = 'playback quality'
    elif secondary == 'buffer':
        yt1_data = yt1_har.plot_rbuf_time()
        yt2_data = yt2_har.plot_rbuf_time()
        statistic = 'Buffer (Seconds)'
        line_chart.secondary_range = (0, 150)
    elif secondary:
        raise NotImplementedError(f'Secondary parameter {secondary} not supported')
    if secondary:
        yt1_data, yt2_data = _shift(data_1=yt1_data,
                                    data_2=yt2_data,
                                    start_1=yt1_start,
                                    start_2=yt2_start,
                                    annotate=False,
                                    line_chart=line_chart)
        line_chart.add(f'YouTube 1', yt1_data, secondary=True)
        line_chart.add(f'Youtube 2', yt2_data, secondary=True)

    # plot everything
    folder = join(OUTPUT_DIR, NAME)
    if not os.path.exists(folder):
        os.mkdir(folder)

    if secondary:
        path = join(folder, f'{primary}_{secondary}')
    else:
        path = join(folder, f'{primary}')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')


def get_vimeo_buffer(NAME):
    """Vimeo doesn't send any data about its buffer to the server so the harparser can't give us any data either.
    Thankfully we have metadata created by Vimeoextractor"""
    vimeo_buffer_file = join(HAR_DIR, 'vimeo_'+NAME+'_bufferdata.json')
    buffer = load(open(vimeo_buffer_file))
    return [(element['time'], element['buffer']) for element in buffer]


def plot(NAME, primary, secondary=None, annotated=False, annotate=True, omit_secondary_vimeo=False):
    """All the plotting needed. If you have a vimeo and a youtube video, this is the function you want to use

    omit_secondary_vimeo: don't show vimeos buffer. only ussed if primary or secondary arg is 'buffer'
    """

    # sanity check
    args = ['mb', 'bandwidth', 'quality', 'buffer', 'interpolated']
    if primary not in args:
        print(f'Supplied unknown argument {primary}. Expected one of {args}')
        raise NotImplementedError
    if secondary and secondary not in args:
        print(f'Supplied unknown argument {secondary}. Expected one of {args}')
        raise NotImplementedError

    youtube_har = YoutubeHar(join(HAR_DIR,  NAME + '_har.json'))
    youtube_meta = join(HAR_DIR, 'youtube_' + NAME + '_metadata.json')


    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True,
                          x_title='Time (sec)',
                          dots_size=0,
                          stroke_style={'width': 3})

    #line_chart.interpolate = 'cubic'

    if primary in ['bandwidth', 'interpolated'] and secondary == 'buffer':
        line_chart.secondary_range = (0, 50)

    # primary metric bandwidth
    youtube_data = youtube_har.plot_bandwidth_interpolated()
    line_chart.y_title = 'Bandwidth (Mbit/s)'
    line_chart.range = (0, 5)
    line_chart.add('YouTube', youtube_data)

    # secondary metric buffer
    yt1_data = youtube_har.plot_rbuf_time()
    line_chart.add('YouTube buffer (in Seconds)', yt1_data, secondary=True)

    # plot everything
    folder = join(OUTPUT_DIR, NAME)
    if not os.path.exists(folder):
        os.mkdir(folder)

    if secondary:
        path = join(folder, f'{primary}_{secondary}')
    else:
        path = join(folder, f'{primary}')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')
    print(f'Created plot at: {path}.png')



if __name__ == '__main__':
    # plot_vimeo_quality_vs_time('vimeo_e2')

    # experiments = ['2yt_delayed_long', '2yt_delayed_long_2', '2yt_delayed_long_3']
    #
    # for NAME in experiments:
    #
    #     plot_2youtube(NAME, primary='mb')
    #     plot_2youtube(NAME, primary='bandwidth')
    #     plot_2youtube(NAME, primary='quality')
    #     plot_2youtube(NAME, primary='quality', secondary='buffer')

    # NAMES = ['combined_long_e1', 'combined_long_e2']
    # for NAME in NAMES:
    #     plot_combined(NAME, primary='mb')
    #     plot_combined(NAME, primary='bandwidth')
    #     plot_combined(NAME, primary='quality')
    #     plot_combined(NAME, primary='quality', secondary='buffer')

    # NAME = 'youtube_first_1'
    # plot_combined(NAME, primary='mb')
    #
    # plot_combined(NAME, primary='interpolated')
    # plot_combined(NAME, primary='interpolated', secondary='buffer', omit_secondary_vimeo=True)
    #
    # plot_combined(NAME, primary='quality')

    # NAME = '2yt_delayed_e3'
    # plot_2youtube(NAME, primary='interpolated')
    # plot_2youtube(NAME, primary='mb')
    # plot_2youtube(NAME, primary='quality')

    plot('youtube_e2', primary='bandwidth', secondary='buffer')