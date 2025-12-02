
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET

@csrf_exempt
def soap_view(request):
    if request.method == "GET":
        # NOTE: Real XML (no &lt;/&gt;), no leading whitespace before the XML declaration.
        wsdl = """<?xml version="1.0" encoding="UTF-8"?>
<definitions name="CalculatorService"
    targetNamespace="http://example.com/"
    xmlns="http://schemas.xmlsoap.org/wsdl/"
    xmlns:tns="http://example.com/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema">

    <message name="AddRequest">
        <part name="a" type="xsd:int"/>
        <part name="b" type="xsd:int"/>
    </message>

    <message name="AddResponse">
        <part name="result" type="xsd:int"/>
    </message>

    <portType name="CalculatorPortType">
        <operation name="Add">
            <input message="tns:AddRequest"/>
            <output message="tns:AddResponse"/>
        </operation>
    </portType>

    <binding name="CalculatorBinding" type="tns:CalculatorPortType">
        <soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="Add">
            Add
            <input>
                <soap:body use="literal"/>
            </input>
            <output>
                <soap:body use="literal"/>
            </output>
        </operation>
    </binding>

    <service name="CalculatorService">
        <port name="CalculatorPort" binding="tns:CalculatorBinding">
            <soap:address location="http://127.0.0.1:8000/soap/"/>
        </port>
    </service>
</definitions>
"""
        # .strip() ensures no trailing/leading whitespace sneaks in.
        return HttpResponse(wsdl.strip(), content_type="text/xml; charset=utf-8")

    if request.method == "POST":
        try:
            # Parse the incoming SOAP request
            tree = ET.fromstring(request.body)
            a_node = tree.find('.//a')
            b_node = tree.find('.//b')
            if a_node is None or b_node is None:
                return HttpResponse("Missing <a> or <b>", status=400)

            a = int(a_node.text)
            b = int(b_node.text)
            result = a + b

            # Proper SOAP 1.1 response envelope (no escaping, no leading newline)
            soap_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <AddResponse>
      <result>{result}</result>
    </AddResponse>
  </soap:Body>
</soap:Envelope>"""

            return HttpResponse(soap_response.strip(), content_type="text/xml; charset=utf-8")
        except ET.ParseError:
            return HttpResponse("Invalid XML", status=400)
        except (TypeError, ValueError):
            return HttpResponse("Invalid number format", status=400)

    return HttpResponse("Method not allowed", status=405)
