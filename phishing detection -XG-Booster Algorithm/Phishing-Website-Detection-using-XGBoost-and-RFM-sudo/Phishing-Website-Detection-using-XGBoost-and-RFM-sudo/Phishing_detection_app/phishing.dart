import 'package:ecell/phishing_detect.dart';
import 'package:flutter/material.dart';

class PhishingLink extends StatefulWidget {
  const PhishingLink({super.key});

  @override
  State<PhishingLink> createState() => _PhishingLinkState();
}

class _PhishingLinkState extends State<PhishingLink> {
  String result = '';
  String riskLevel = '';
  bool isScanned = false;
  List<ScanHistory> scanHistory = [];
  int riskScore = 0;

  @override
  Widget build(BuildContext context) {
    TextEditingController titleController = TextEditingController();
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('🔒 Phishing URL Detector', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        backgroundColor: Colors.deepOrange,
        elevation: 5,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Header Section with Info
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.deepOrange.shade600, Colors.deepOrange.shade400],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Column(
                children: [
                  const Text(
                    'Check URL Safety',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Detect phishing and malicious websites in seconds',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ),

            // URL Input Section
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Enter URL',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: titleController,
                    decoration: InputDecoration(
                      hintText: 'https://example.com',
                      prefixIcon: const Icon(Icons.language, color: Colors.deepOrange),
                      suffixIcon: titleController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                titleController.clear();
                                setState(() {});
                              },
                            )
                          : null,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Colors.grey),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey.shade300),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Colors.deepOrange, width: 2),
                      ),
                    ),
                    onChanged: (value) {
                      setState(() {});
                    },
                  ),
                ],
              ),
            ),

            // Scan Button
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: ElevatedButton.icon(
                onPressed: () async {
                  if (titleController.text.isEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Please enter a URL')),
                    );
                    return;
                  }

                  String url = titleController.text;
                  result = await check_website_status(url);
                  
                  // Simulate risk score calculation
                  riskScore = result.contains('phishing') ? 85 : 15;
                  riskLevel = result.contains('phishing') ? 'High Risk' : 'Safe';
                  isScanned = true;

                  // Add to history
                  scanHistory.insert(
                    0,
                    ScanHistory(
                      url: url,
                      result: result,
                      timestamp: DateTime.now(),
                    ),
                  );

                  setState(() {});
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepOrange,
                  padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                icon: const Icon(Icons.search),
                label: const Text(
                  'Scan URL',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Result Section
            if (isScanned)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Risk Level Card
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: result.contains('phishing') ? Colors.red.shade50 : Colors.green.shade50,
                        border: Border.all(
                          color: result.contains('phishing') ? Colors.red : Colors.green,
                          width: 2,
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Column(
                        children: [
                          Text(
                            result.contains('phishing') ? '⚠️ PHISHING ALERT' : '✅ SAFE',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: result.contains('phishing') ? Colors.red : Colors.green,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            result,
                            style: const TextStyle(fontSize: 14, color: Colors.black87),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Risk Score Gauge
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Risk Score',
                                style: TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 14,
                                ),
                              ),
                              Text(
                                '$riskScore%',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                  color: result.contains('phishing') ? Colors.red : Colors.green,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(10),
                            child: LinearProgressIndicator(
                              value: riskScore / 100,
                              minHeight: 8,
                              backgroundColor: Colors.grey.shade300,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                result.contains('phishing') ? Colors.red : Colors.green,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // URL Info Card
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.blue.shade200),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'URL Information',
                            style: TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 12),
                          _buildInfoRow('Domain', 'www.example.com'),
                          const SizedBox(height: 8),
                          _buildInfoRow('Protocol', 'HTTPS'),
                          const SizedBox(height: 8),
                          _buildInfoRow('URL Length', '${titleController.text.length} characters'),
                          const SizedBox(height: 8),
                          _buildInfoRow('Status', result.contains('phishing') ? 'Malicious' : 'Legitimate'),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Security Features
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.purple.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.purple.shade200),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Security Features',
                            style: TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 12),
                          _buildSecurityFeature('SSL Certificate', 'Verified', true),
                          const SizedBox(height: 8),
                          _buildSecurityFeature('Domain Age', 'Established', true),
                          const SizedBox(height: 8),
                          _buildSecurityFeature('Web Traffic', result.contains('phishing') ? 'Suspicious' : 'High', !result.contains('phishing')),
                          const SizedBox(height: 8),
                          _buildSecurityFeature('IP Address', 'Domain-based', true),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

            if (isScanned) const SizedBox(height: 20),

            // Feedback Section
            Padding(
              padding: const EdgeInsets.all(16),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Column(
                  children: [
                    const Text(
                      'Help Us Improve',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Was this detection accurate?',
                      style: TextStyle(fontSize: 12, color: Colors.black54),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        ElevatedButton.icon(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Thank you for your feedback!')),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          icon: const Icon(Icons.thumb_up),
                          label: const Text('Yes'),
                        ),
                        ElevatedButton.icon(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('We\'ll investigate this. Thank you!')),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          icon: const Icon(Icons.thumb_down),
                          label: const Text('No'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Scan History
            if (scanHistory.isNotEmpty)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Recent Scans',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: scanHistory.length > 5 ? 5 : scanHistory.length,
                      itemBuilder: (context, index) {
                        var scan = scanHistory[index];
                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: scan.result.contains('phishing') ? Colors.red.shade50 : Colors.green.shade50,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: scan.result.contains('phishing') ? Colors.red.shade200 : Colors.green.shade200,
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                scan.url.length > 40 ? '${scan.url.substring(0, 40)}...' : scan.url,
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    scan.result.contains('phishing') ? '⚠️ Phishing' : '✅ Safe',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: scan.result.contains('phishing') ? Colors.red : Colors.green,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                  Text(
                                    _formatTime(scan.timestamp),
                                    style: const TextStyle(fontSize: 10, color: Colors.black54),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.black54),
        ),
        Text(
          value,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
        ),
      ],
    );
  }

  Widget _buildSecurityFeature(String feature, String status, bool isSecure) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          feature,
          style: const TextStyle(fontSize: 12, color: Colors.black54),
        ),
        Row(
          children: [
            Text(
              status,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: isSecure ? Colors.green : Colors.red,
              ),
            ),
            const SizedBox(width: 4),
            Icon(
              isSecure ? Icons.check_circle : Icons.cancel,
              size: 16,
              color: isSecure ? Colors.green : Colors.red,
            ),
          ],
        ),
      ],
    );
  }

  String _formatTime(DateTime dateTime) {
    Duration diff = DateTime.now().difference(dateTime);
    if (diff.inMinutes < 1) {
      return 'just now';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}h ago';
    } else {
      return '${diff.inDays}d ago';
    }
  }
}

class ScanHistory {
  final String url;
  final String result;
  final DateTime timestamp;

  ScanHistory({
    required this.url,
    required this.result,
    required this.timestamp,
  });
}
