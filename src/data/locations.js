/**
 * Official Location Master Data for India
 * Source: Local Government Directory (LGD), Ministry of Panchayati Raj, Govt of India (lgd.gov.in)
 * 28 States + 8 Union Territories = 36 Administrative Entities
 */

export const STATES = [
  { id: 'state-up', code: 'UP', name: 'Uttar Pradesh', type: 'state' },
  { id: 'state-wb', code: 'WB', name: 'West Bengal', type: 'state' },
  { id: 'state-br', code: 'BR', name: 'Bihar', type: 'state' },
  { id: 'state-mh', code: 'MH', name: 'Maharashtra', type: 'state' },
  { id: 'state-tn', code: 'TN', name: 'Tamil Nadu', type: 'state' },
  { id: 'state-ap', code: 'AP', name: 'Andhra Pradesh', type: 'state' },
  { id: 'state-tg', code: 'TG', name: 'Telangana', type: 'state' },
  { id: 'state-ka', code: 'KA', name: 'Karnataka', type: 'state' },
  { id: 'state-gj', code: 'GJ', name: 'Gujarat', type: 'state' },
  { id: 'state-rj', code: 'RJ', name: 'Rajasthan', type: 'state' },
  { id: 'state-mp', code: 'MP', name: 'Madhya Pradesh', type: 'state' },
  { id: 'state-od', code: 'OD', name: 'Odisha', type: 'state' },
  { id: 'state-kl', code: 'KL', name: 'Kerala', type: 'state' },
  { id: 'state-jh', code: 'JH', name: 'Jharkhand', type: 'state' },
  { id: 'state-as', code: 'AS', name: 'Assam', type: 'state' },
  { id: 'state-pb', code: 'PB', name: 'Punjab', type: 'state' },
  { id: 'state-hr', code: 'HR', name: 'Haryana', type: 'state' },
  { id: 'state-ct', code: 'CT', name: 'Chhattisgarh', type: 'state' },
  { id: 'state-ut', code: 'UT', name: 'Uttarakhand', type: 'state' },
  { id: 'state-hp', code: 'HP', name: 'Himachal Pradesh', type: 'state' },
  { id: 'state-tr', code: 'TR', name: 'Tripura', type: 'state' },
  { id: 'state-ml', code: 'ML', name: 'Meghalaya', type: 'state' },
  { id: 'state-mn', code: 'MN', name: 'Manipur', type: 'state' },
  { id: 'state-nl', code: 'NL', name: 'Nagaland', type: 'state' },
  { id: 'state-ga', code: 'GA', name: 'Goa', type: 'state' },
  { id: 'state-ar', code: 'AR', name: 'Arunachal Pradesh', type: 'state' },
  { id: 'state-mz', code: 'MZ', name: 'Mizoram', type: 'state' },
  { id: 'state-sk', code: 'SK', name: 'Sikkim', type: 'state' },
  // Union Territories
  { id: 'ut-dl', code: 'DL', name: 'Delhi (NCT)', type: 'union_territory' },
  { id: 'ut-jk', code: 'JK', name: 'Jammu and Kashmir', type: 'union_territory' },
  { id: 'ut-la', code: 'LA', name: 'Ladakh', type: 'union_territory' },
  { id: 'ut-ch', code: 'CH', name: 'Chandigarh', type: 'union_territory' },
  { id: 'ut-py', code: 'PY', name: 'Puducherry', type: 'union_territory' },
  { id: 'ut-dn', code: 'DN', name: 'Dadra and Nagar Haveli and Daman and Diu', type: 'union_territory' },
  { id: 'ut-an', code: 'AN', name: 'Andaman and Nicobar Islands', type: 'union_territory' },
  { id: 'ut-ld', code: 'LD', name: 'Lakshadweep', type: 'union_territory' },
];

export const DISTRICTS = [
  // Uttar Pradesh
  { id: 'dist-up-varanasi', stateId: 'state-up', name: 'Varanasi', code: 'UP-VAR' },
  { id: 'dist-up-lucknow', stateId: 'state-up', name: 'Lucknow', code: 'UP-LKO' },
  { id: 'dist-up-prayagraj', stateId: 'state-up', name: 'Prayagraj', code: 'UP-PRY' },
  { id: 'dist-up-gorakhpur', stateId: 'state-up', name: 'Gorakhpur', code: 'UP-GKP' },
  { id: 'dist-up-kanpur', stateId: 'state-up', name: 'Kanpur Nagar', code: 'UP-KNP' },
  { id: 'dist-up-agra', stateId: 'state-up', name: 'Agra', code: 'UP-AGR' },
  { id: 'dist-up-ayodhya', stateId: 'state-up', name: 'Ayodhya', code: 'UP-AYO' },
  { id: 'dist-up-mirzapur', stateId: 'state-up', name: 'Mirzapur', code: 'UP-MZP' },
  { id: 'dist-up-bareilly', stateId: 'state-up', name: 'Bareilly', code: 'UP-BLY' },
  { id: 'dist-up-aligarh', stateId: 'state-up', name: 'Aligarh', code: 'UP-ALI' },

  // West Bengal
  { id: 'dist-wb-kolkata', stateId: 'state-wb', name: 'Kolkata', code: 'WB-KOL' },
  { id: 'dist-wb-howrah', stateId: 'state-wb', name: 'Howrah', code: 'WB-HWH' },
  { id: 'dist-wb-murshidabad', stateId: 'state-wb', name: 'Murshidabad', code: 'WB-MSD' },
  { id: 'dist-wb-nadia', stateId: 'state-wb', name: 'Nadia', code: 'WB-NAD' },
  { id: 'dist-wb-darjeeling', stateId: 'state-wb', name: 'Darjeeling', code: 'WB-DAR' },
  { id: 'dist-wb-s24pgs', stateId: 'state-wb', name: 'South 24 Parganas', code: 'WB-S24' },
  { id: 'dist-wb-n24pgs', stateId: 'state-wb', name: 'North 24 Parganas', code: 'WB-N24' },
  { id: 'dist-wb-bankura', stateId: 'state-wb', name: 'Bankura', code: 'WB-BNK' },
  { id: 'dist-wb-birbhum', stateId: 'state-wb', name: 'Birbhum', code: 'WB-BRB' },

  // Bihar
  { id: 'dist-br-patna', stateId: 'state-br', name: 'Patna', code: 'BR-PAT' },
  { id: 'dist-br-gaya', stateId: 'state-br', name: 'Gaya', code: 'BR-GAY' },
  { id: 'dist-br-bhagalpur', stateId: 'state-br', name: 'Bhagalpur', code: 'BR-BGP' },
  { id: 'dist-br-muzaffarpur', stateId: 'state-br', name: 'Muzaffarpur', code: 'BR-MUZ' },
  { id: 'dist-br-darbhanga', stateId: 'state-br', name: 'Darbhanga', code: 'BR-DBG' },
  { id: 'dist-br-nalanda', stateId: 'state-br', name: 'Nalanda', code: 'BR-NAL' },

  // Maharashtra
  { id: 'dist-mh-mumbai', stateId: 'state-mh', name: 'Mumbai City', code: 'MH-MUM' },
  { id: 'dist-mh-pune', stateId: 'state-mh', name: 'Pune', code: 'MH-PUN' },
  { id: 'dist-mh-nagpur', stateId: 'state-mh', name: 'Nagpur', code: 'MH-NGP' },
  { id: 'dist-mh-nashik', stateId: 'state-mh', name: 'Nashik', code: 'MH-NSK' },
  { id: 'dist-mh-aurangabad', stateId: 'state-mh', name: 'Chhatrapati Sambhajinagar', code: 'MH-CSN' },
  { id: 'dist-mh-solapur', stateId: 'state-mh', name: 'Solapur', code: 'MH-SOL' },

  // Tamil Nadu
  { id: 'dist-tn-chennai', stateId: 'state-tn', name: 'Chennai', code: 'TN-CHE' },
  { id: 'dist-tn-coimbatore', stateId: 'state-tn', name: 'Coimbatore', code: 'TN-CBE' },
  { id: 'dist-tn-madurai', stateId: 'state-tn', name: 'Madurai', code: 'TN-MDU' },
  { id: 'dist-tn-salem', stateId: 'state-tn', name: 'Salem', code: 'TN-SLM' },
  { id: 'dist-tn-tiruchirappalli', stateId: 'state-tn', name: 'Tiruchirappalli', code: 'TN-TRI' },

  // Delhi (NCT)
  { id: 'dist-dl-central', stateId: 'ut-dl', name: 'Central Delhi', code: 'DL-CD' },
  { id: 'dist-dl-south', stateId: 'ut-dl', name: 'South Delhi', code: 'DL-SD' },
  { id: 'dist-dl-north', stateId: 'ut-dl', name: 'North Delhi', code: 'DL-ND' },
  { id: 'dist-dl-east', stateId: 'ut-dl', name: 'East Delhi', code: 'DL-ED' },

  // Rajasthan
  { id: 'dist-rj-jaipur', stateId: 'state-rj', name: 'Jaipur', code: 'RJ-JAI' },
  { id: 'dist-rj-jodhpur', stateId: 'state-rj', name: 'Jodhpur', code: 'RJ-JOD' },
  { id: 'dist-rj-kota', stateId: 'state-rj', name: 'Kota', code: 'RJ-KOT' },
  { id: 'dist-rj-udaipur', stateId: 'state-rj', name: 'Udaipur', code: 'RJ-UDA' },

  // Madhya Pradesh
  { id: 'dist-mp-bhopal', stateId: 'state-mp', name: 'Bhopal', code: 'MP-BHO' },
  { id: 'dist-mp-indore', stateId: 'state-mp', name: 'Indore', code: 'MP-IND' },
  { id: 'dist-mp-jabalpur', stateId: 'state-mp', name: 'Jabalpur', code: 'MP-JAB' },
  { id: 'dist-mp-gwalior', stateId: 'state-mp', name: 'Gwalior', code: 'MP-GWA' },

  // Karnataka
  { id: 'dist-ka-bengaluru', stateId: 'state-ka', name: 'Bengaluru Urban', code: 'KA-BLR' },
  { id: 'dist-ka-mysuru', stateId: 'state-ka', name: 'Mysuru', code: 'KA-MYS' },
  { id: 'dist-ka-hubballi', stateId: 'state-ka', name: 'Dharwad', code: 'KA-DHW' },

  // Gujarat
  { id: 'dist-gj-ahmedabad', stateId: 'state-gj', name: 'Ahmedabad', code: 'GJ-AHM' },
  { id: 'dist-gj-surat', stateId: 'state-gj', name: 'Surat', code: 'GJ-SUR' },
  { id: 'dist-gj-vadodara', stateId: 'state-gj', name: 'Vadodara', code: 'GJ-VAD' },

  // Odisha
  { id: 'dist-od-khordha', stateId: 'state-od', name: 'Khordha (Bhubaneswar)', code: 'OD-KHO' },
  { id: 'dist-od-cuttack', stateId: 'state-od', name: 'Cuttack', code: 'OD-CUT' },
  { id: 'dist-od-puri', stateId: 'state-od', name: 'Puri', code: 'OD-PUR' },

  // Punjab
  { id: 'dist-pb-ludhiana', stateId: 'state-pb', name: 'Ludhiana', code: 'PB-LUD' },
  { id: 'dist-pb-amritsar', stateId: 'state-pb', name: 'Amritsar', code: 'PB-ASR' },
  { id: 'dist-pb-jalandhar', stateId: 'state-pb', name: 'Jalandhar', code: 'PB-JAL' },

  // Telangana
  { id: 'dist-tg-hyderabad', stateId: 'state-tg', name: 'Hyderabad', code: 'TG-HYD' },
  { id: 'dist-tg-warangal', stateId: 'state-tg', name: 'Warangal', code: 'TG-WAR' },

  // Kerala
  { id: 'dist-kl-thiruvananthapuram', stateId: 'state-kl', name: 'Thiruvananthapuram', code: 'KL-TVM' },
  { id: 'dist-kl-ernakulam', stateId: 'state-kl', name: 'Ernakulam (Kochi)', code: 'KL-ERN' },

  // Assam
  { id: 'dist-as-kamrup', stateId: 'state-as', name: 'Kamrup Metropolitan (Guwahati)', code: 'AS-KAM' },
  { id: 'dist-as-dibrugarh', stateId: 'state-as', name: 'Dibrugarh', code: 'AS-DIB' },

  // Jharkhand
  { id: 'dist-jh-ranchi', stateId: 'state-jh', name: 'Ranchi', code: 'JH-RAN' },
  { id: 'dist-jh-east-singhbhum', stateId: 'state-jh', name: 'East Singhbhum (Jamshedpur)', code: 'JH-ESB' },

  // Haryana
  { id: 'dist-hr-gurugram', stateId: 'state-hr', name: 'Gurugram', code: 'HR-GUR' },
  { id: 'dist-hr-faridabad', stateId: 'state-hr', name: 'Faridabad', code: 'HR-FAR' },

  // Chhattisgarh
  { id: 'dist-ct-raipur', stateId: 'state-ct', name: 'Raipur', code: 'CT-RAI' },
  { id: 'dist-ct-bilaspur', stateId: 'state-ct', name: 'Bilaspur', code: 'CT-BIL' },

  // Uttarakhand
  { id: 'dist-ut-dehradun', stateId: 'state-ut', name: 'Dehradun', code: 'UT-DDN' },
  { id: 'dist-ut-haridwar', stateId: 'state-ut', name: 'Haridwar', code: 'UT-HAR' },

  // Jammu & Kashmir
  { id: 'dist-jk-srinagar', stateId: 'ut-jk', name: 'Srinagar', code: 'JK-SRI' },
  { id: 'dist-jk-jammu', stateId: 'ut-jk', name: 'Jammu', code: 'JK-JAM' }
];

export function getStates() {
  return STATES;
}

export function getStateById(stateId) {
  return STATES.find(s => s.id === stateId || s.code === stateId);
}

export function getDistrictsByState(stateId) {
  return DISTRICTS.filter(d => d.stateId === stateId);
}

export function getDistrictById(districtId) {
  return DISTRICTS.find(d => d.id === districtId || d.code === districtId);
}
