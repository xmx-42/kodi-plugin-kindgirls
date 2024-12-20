# -*- coding: utf-8 -*-
# MP 241205 seems to work ..

import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from urllib.parse import urlencode, parse_qs
from resources.lib.kindgirls import KindGirls

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')
addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])
addon_args = parse_qs(sys.argv[2][1:])

def log(msg):
    xbmc.log((u"### [%s] - %s" % (addon_name, msg,)), level=xbmc.LOGDEBUG)


def notify(title, msg):
    xbmc.executebuiltin('XBMC.Notification(' + title + ',' + msg + ',10)')


def getAddonUrl(params, **kwargs):
    params.update(kwargs)
    return "%s?&%s" % (addon_url, urlencode(params))


def getAddonParam(name):
    return (lambda val: None if val is None else val[0])(addon_args.get(name, None))


KindGirls = KindGirls()
Mode = getAddonParam('mode')

if Mode is None:
    itemMonth = xbmcgui.ListItem(label='Galleries by month')
    itemCountry = xbmcgui.ListItem(label='Galleries by country')
    itemAlphabet = xbmcgui.ListItem(label='Galleries by letter')
    itemRandom = xbmcgui.ListItem(label='Random gallery')
    itemVideo = xbmcgui.ListItem(label='Video gallery')

    xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'month'}), itemMonth, True)
    xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'country'}), itemCountry, True)
    xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'letter'}), itemAlphabet, True)
    xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'random'}), itemRandom, True)
    xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'video'}), itemVideo, True)


elif Mode == 'month':
    Month = getAddonParam('month')

    if Month is None:
        Months = KindGirls.GetMonths()

        for Month in Months:
            item = xbmcgui.ListItem(Month['Name'])
            xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'month', 'month': Month['Date']}), item, True)
    else:
        Galleries = KindGirls.GetMonthGalleries(Month)

        for Gallery in Galleries:
            item = xbmcgui.ListItem(label=Gallery['Title'])
            # MP 241126 to get thumbnail of gallery > OK in month gal
            item.setArt({'thumb': Gallery['Img']})
            xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'gallery', 'url': Gallery['Url']}), item, True)


elif Mode == 'country' or Mode == 'letter':
    Id = getAddonParam(Mode)

    if Id is None:
        if Mode == 'country':
            Items = KindGirls.GetCountries()
        elif Mode == 'letter':
            Items = KindGirls.GetLetters()

        for Item in Items:
            item = xbmcgui.ListItem(Item['Name'])

            if Mode == 'country':
                Url = getAddonUrl({'mode': Mode, 'country': Item['Id']})
            elif Mode == 'letter':
                Url = getAddonUrl({'mode': Mode, 'letter': Item['Id']})

            xbmcplugin.addDirectoryItem(addon_handle, Url, item, True)
    else:
        if Mode == 'country':
            Girls = KindGirls.GetGirls(country=Id)
        elif Mode == 'letter':
            Girls = KindGirls.GetGirls(letter=Id)

        for Girl in Girls:
            item = xbmcgui.ListItem(label=Girl['Title'])
            # MP 241126 to get thumbnail of gallery > OK
            item.setArt({'thumb': Girl['Img']})
            xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'girl', 'url': Girl['Url']}), item, True)


elif Mode == 'girl':
    Url = getAddonParam('url')
    Galleries = KindGirls.GetGirlGalleries(Url)

    for Gallery in Galleries:
        item = xbmcgui.ListItem(label=Gallery['Title'])
        # MP 241126 to get thumbnail of gallery > OK
        item.setArt({'thumb': Gallery['Img']})
        xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'gallery', 'url': Gallery['Url']}), item, True)


elif Mode == 'random':
# same as Mode == 'girl' works 
#    Url = getAddonParam('url')
    Url = 'https://www.kindgirls.com/old/r'   # quick&dirty MP
    Galleries = KindGirls.GetGirlGalleries(Url)

    for Gallery in Galleries:
#        item = xbmcgui.ListItem(label=Gallery['Title'])
        item = xbmcgui.ListItem(label=Gallery['Name'])
        # label with 'Name' as added item in list > OK
        # MP 241126 to get thumbnail of gallery > OK
        item.setArt({'thumb': Gallery['Img']})
        xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'gallery', 'url': Gallery['Url']}), item, True)


elif Mode == 'gallery':
    GalleryUrl = getAddonParam('url')

    if (GalleryUrl is not None):
        GalleryUrl = GalleryUrl
        Gallery = KindGirls.GetGallery(GalleryUrl)

        if (Gallery):
            for Image in Gallery:
                if 'Title' in Image:
                    item = xbmcgui.ListItem(label=Image['Title'])
                    # MP 241127 to get thumbnail of gallery > OK
                    item.setArt({'thumb': Image['ThumbUrl']})
                    xbmcplugin.addDirectoryItem(addon_handle, Image['PhotoUrl'], item)
                else:
                    item = xbmcgui.ListItem(label="More galleries %s" % Image['Name'])
                    xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'girl', 'url': Image['Url']}), item, True)


elif Mode == 'video':
    Page = getAddonParam('page')

    if Page is None:
        Page = 1

    Gallery = KindGirls.GetVideoGallery(Page)

    if (Gallery):
        for Video in Gallery:
            if 'NextPage' in Video:
                item = xbmcgui.ListItem(label='Next page (' + Video['NextPage'] + ')')
                xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'video', 'page': Video['NextPage']}), item, True)
            else:
#                item = xbmcgui.ListItem(Video['Title'], iconImage='DefaultVideo.png', thumbnailImage=Video['ThumbUrl'])
                item = xbmcgui.ListItem(label=Video['Title'])
                item.setInfo(type='Video', infoLabels={'Title': Video['Title']})
                # MP 241122 to get thumbnail of video
                # following https://alwinesch.github.io/group__python__xbmcgui__listitem.html
                item.setArt({'thumb': Video['ThumbUrl']})
                # OK
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(addon_handle, getAddonUrl({'mode': 'video_play', 'url': Video['Url']}), item)


elif Mode == 'video_play':
    Url = getAddonParam('url')
    VideoUrl = KindGirls.GetVideoUrl(Url)

    if VideoUrl is None:
        notify('Error', 'Not found video')
    else:
        item = xbmcgui.ListItem(path=VideoUrl)
        xbmcplugin.setResolvedUrl(addon_handle, True, item)


xbmcplugin.endOfDirectory(addon_handle)
