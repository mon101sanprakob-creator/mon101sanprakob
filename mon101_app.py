geolocator 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:maps_toolkit/maps_toolkit.dart' as mp;

void main() => runApp(const MapMeasurementApp());

class MapMeasurementApp extends StatelessWidget {
  const MapMeasurementApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: MapScreen(),
    );
  }
}

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  Completer<GoogleMapController> _controller = Completer();
  
  // พิกัดเริ่มต้น (กรุงเทพฯ) - จะเปลี่ยนเป็นพิกัดจริงเมื่อ GPS ทำงาน
  static const CameraPosition _initialPosition = CameraPosition(
    target: LatLng(13.7563, 100.5018),
    zoom: 15,
  );

  Position? _currentPosition;
  Set<Marker> _markers = {};
  List<LatLng> _polygonPoints = [];
  Set<Polygon> _polygons = {};
  String _calculatedAreaText = "ยังไม่ได้คำนวณพื้นที่";
  bool _isDrawingFinished = false;

  @override
  void initState() {
    super.initState();
    _determinePosition();
  }

  // ฟังก์ชันดึงตำแหน่ง Real-time GPS
  Future<void> _determinePosition() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    // ติดตามตำแหน่ง Real-time
    Geolocator.getPositionStream(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high, distanceFilter: 2)
    ).listen((Position position) async {
      final GoogleMapController controller = await _controller.future;
      
      setState(() {
        _currentPosition = position;
        // อัปเดตมุดบอกตำแหน่งปัจจุบัน
        _markers.add(
          Marker(
            markerId: const MarkerId('current_location'),
            position: LatLng(position.latitude, position.longitude),
            infoWindow: const InfoWindow(title: 'ตำแหน่งของคุณ'),
          ),
        );
      });

      // เลื่อนหน้าจอตามผู้ใช้แบบ Real-time
      controller.animateCamera(CameraUpdate.newLatLng(
        LatLng(position.latitude, position.longitude),
      ));
    });
  }

  // ฟังก์ชันเมื่อผู้ใช้จิ้มบนแผนที่เพื่อลากเส้น/ต่อจุด
  void _onMapTap(LatLng point) {
    if (_isDrawingFinished) return; // ถ้ากดเพิ่มพื้นที่เสร็จแล้ว จะไม่ยอมให้จุดเพิ่ม จนกว่าจะล้างค่า

    setState(() {
      _polygonPoints.add(point);
      
      // เพิ่มหมุดสีแดงตามจุดที่จิ้มลากเส้น
      _markers.add(
        Marker(
          markerId: MarkerId(point.toString()),
          position: point,
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
        ),
      );

      // วาดรูปปิดล้อม (Polygon) อัตโนมัติเพื่อให้เห็นพื้นที่ที่ลากเส้น
      _polygons.add(
        Polygon(
          polygonId: const PolygonId('measure_polygon'),
          points: _polygonPoints,
          strokeWidth: 3,
          strokeColor: Colors.blue,
          fillColor: Colors.blue.withOpacity(0.3),
        ),
      );
    });
  }

  // ฟังก์ชันยืนยันการลากเส้นและคำนวณพื้นที่ (แปลงเป็น ไร่-งาน-ตารางวา)
  void _confirmAndCalculateArea() {
    if (_polygonPoints.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('กรุณาจุดตำแหน่งให้มากกว่า 3 จุดขึ้นไปเพื่อคำนวณพื้นที่')),
      );
      return;
    }

    // แปลงพิกัดเป็นรูปแบบของ maps_toolkit
    List<mp.LatLng> mpPoints = _polygonPoints
        .map((p) => mp.LatLng(p.latitude, p.longitude))
        .toList();

    // คำนวณพื้นที่เป็น "ตารางเมตร"
    double areaInSquareMeters = mp.SphericalUtil.computeArea(mpPoints).toDouble();

    // แปลง ตารางเมตร เป็น ตารางวา (1 ตารางวา = 4 ตารางเมตร)
    double totalSquareWa = areaInSquareMeters / 4;

    // คำนวณเป็น ไร่ งาน ตารางวา
    int rai = (totalSquareWa / 400).floor();
    double remainingAfterRai = totalSquareWa % 400;
    
    int ngan = (remainingAfterRai / 100).floor();
    double wa = remainingAfterRai % 100;

    setState(() {
      _isDrawingFinished = true;
      _calculatedAreaText = "พื้นที่: $rai ไร่  $ngan งาน  ${wa.toStringAsFixed(1)} ตารางวา";
    });
  }

  // ฟังก์ชันล้างค่าเพื่อเริ่มวาดใหม่
  void _clearSelection() {
    setState(() {
      _polygonPoints.clear();
      _polygons.clear();
      // ลบหมุดหมุดอื่น ๆ ออก ยกเว้นหมุดตำแหน่ง GPS ปัจจุบัน
      _markers.removeWhere((m) => m.markerId.value != 'current_location');
      _calculatedAreaText = "ยังไม่ได้คำนวณพื้นที่";
      _isDrawingFinished = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('แอปวัดพื้นที่ดินด้วย GPS')),
      body: Stack(
        children: [
          // ส่วนแสดงผลแผนที่
          GoogleMap(
            mapType: MapType.satellite, // <--- จุดนี้ทำให้เห็นหลังคาบ้าน (ภาพดาวเทียม)
            initialCameraPosition: _initialPosition,
            markers: _markers,
            polygons: _polygons,
            onMapCreated: (GoogleMapController controller) {
              _controller.complete(controller);
            },
            onTap: _onMapTap, // เรียกฟังก์ชันเมื่อใช้นิ้วจิ้มลากจุดบนแผนที่
            myLocationEnabled: true,
            myLocationButtonEnabled: true,
          ),

          // ส่วนแสดงผลลัพธ์คำนวณพื้นที่ด้านบน
          Positioned(
            top: 20,
            left: 15,
            right: 15,
            child: Card(
              color: Colors.white.withOpacity(0.9),
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  _calculatedAreaText,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ),

          // ปุ่มควบคุมด้านล่าง
          Positioned(
            bottom: 30,
            left: 20,
            right: 20,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: _clearSelection,
                  icon: const Icon(Icons.refresh),
                  label: const Text('เริ่มใหม่'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent, foregroundColor: Colors.white),
                ),
                ElevatedButton.icon(
                  onPressed: _confirmAndCalculateArea,
                  icon: const Icon(Icons.check),
                  label: const Text('ยืนยันลากเส้นเสร็จสิ้น'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green, foregroundColor: Colors.white),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
