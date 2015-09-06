#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import tornado.web
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


contentTypeName = r'Content-Type'
contentTypeValue = r'application/xml;charset=utf-8'


class WeiXunEventHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        signature = self.get_query_argument('signature', None)
        timestamp = self.get_query_argument('timestamp', None)
        nonce = self.get_query_argument('nonce', None)
        echostr = self.get_query_argument('echostr', None)
        self.write(echostr)

    def post(self, *args, **kwargs):
        xml_text = self.request.body.decode('utf-8')
        in_message = self.extract_normal_message_info(xml_text)
        # print(in_message)
        print(type(in_message))
        ret = self.convter_to_xml(in_message)
        print(type(ret))
        if ret:
            self.set_header(contentTypeName, contentTypeValue)
            resstr = ET.tostring(ret, encoding='utf-8', method='xml')
            print(resstr.decode("utf-8"))
            self.write(resstr)
        else:
            self.write("")

    def extract_normal_message_info(self, xml_text):
        root = ET.fromstring(xml_text)
        in_message = dict()
        for child_of_root in root:
            in_message[child_of_root.tag] = child_of_root.text
        return in_message

    def convter_to_xml(self, data_in_dict):
        root = ET.Element("xml")
        for child in data_in_dict:
            subItem = ET.Element(child)
            subItem.text = data_in_dict[child]
            root.append(subItem)
        return root