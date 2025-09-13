# 👤 Customer Data Persistence Feature

## 📋 Overview

The Customer Data Persistence feature allows the web app to remember customer information between orders, automatically prepopulating the checkout form with previously entered data. This improves user experience by reducing the need to re-enter information for repeat customers.

## 🎯 Features

### **Data Persistence**
- **Fields Saved**: First Name, Last Name, Middle Name, Phone Number, Email, City, Address
- **Fields NOT Saved**: Delivery Date, Delivery Method, Pickup Address, Comments
- **Storage Duration**: 1 year (365 days)
- **Storage Method**: Browser localStorage with metadata

### **Automatic Population**
- Form fields are automatically populated when customer returns to checkout
- Data can be edited or cleared by the user
- Only populated if valid data exists and hasn't expired

### **Data Management**
- Automatic expiration handling
- Version migration support
- Cache preservation during app updates
- Debug functions for development

## 🛠️ Technical Implementation

### **Storage Structure**
```javascript
{
  version: "1.0.0",
  timestamp: 1640995200000,
  expiresAt: 1672531200000,
  data: {
    firstName: "Иван",
    lastName: "Иванов", 
    middleName: "Иванович",
    phoneNumber: "+375291234567",
    email: "ivan@example.com",
    city: "Минск",
    addressLine: "ул. Ленина, 1, кв. 5"
  }
}
```

### **Key Functions**

#### **Data Management**
- `createCustomerDataWithMetadata(customerData)` - Creates structured data with metadata
- `loadCustomerDataWithExpiration()` - Loads data with expiration check
- `saveCustomerDataWithMetadata(customerData)` - Saves data with metadata
- `clearCustomerData()` - Removes all customer data

#### **Form Integration**
- `extractCustomerDataFromForm()` - Extracts data from checkout form
- `populateFormWithCustomerData(customerData)` - Populates form with saved data

#### **Utility Functions**
- `checkCustomerDataExpiration()` - Checks if data has expired
- `getCustomerDataAge()` - Returns age of stored data in days

### **Integration Points**

#### **Form Submission**
Customer data is automatically saved when an order is successfully submitted:
```javascript
// Save customer data for future prepopulation
const customerData = extractCustomerDataFromForm();
if (Object.keys(customerData).length > 0) {
    saveCustomerDataWithMetadata(customerData);
}
```

#### **Checkout View Display**
Customer data is automatically loaded when the checkout view is displayed:
```javascript
// Load and populate customer data if available
const customerData = loadCustomerDataWithExpiration();
if (Object.keys(customerData).length > 0) {
    populateFormWithCustomerData(customerData);
}
```

#### **Cache Management**
Customer data is preserved during cache clearing operations:
```javascript
const keysToPreserve = ['cart', 'cart_version', 'app_version', CUSTOMER_DATA_KEY];
```

## 🔧 Configuration

### **Constants**
```javascript
const CUSTOMER_DATA_KEY = 'customer_data';
const CUSTOMER_DATA_VERSION = '1.0.0';
const CUSTOMER_DATA_EXPIRATION_DAYS = 365;
```

### **Field Mappings**
```javascript
const fieldMappings = {
    'firstName': 'first-name',
    'lastName': 'last-name', 
    'middleName': 'middle-name',
    'phoneNumber': 'phone-number',
    'email': 'email',
    'city': 'city',
    'addressLine': 'address-line'
};
```

## 🧪 Testing

### **Unit Tests**
Run customer data tests:
```bash
python3 tests/unit/test_customer_data.py
```

### **Test Coverage**
- ✅ Constants existence
- ✅ Function definitions
- ✅ Form integration
- ✅ Data population
- ✅ Cache preservation
- ✅ Global function exposure
- ✅ Field mappings
- ✅ Expiration logic
- ✅ Versioning system

## 🐛 Debugging

### **Global Functions**
All customer data functions are exposed globally for debugging:
```javascript
// Check customer data
window.loadCustomerDataWithExpiration()

// Save test data
window.saveCustomerDataWithMetadata({
    firstName: "Test",
    lastName: "User",
    email: "test@example.com"
})

// Clear data
window.clearCustomerData()

// Check data age
window.getCustomerDataAge()
```

### **Console Logging**
The feature includes comprehensive console logging:
- 👤 Customer data operations
- 💾 Data saving/loading
- ⏰ Expiration checks
- 🔄 Migration operations
- ❌ Error handling

## 🔒 Privacy & Security

### **Data Storage**
- **Location**: Browser localStorage only
- **Scope**: Per-device, per-browser
- **Access**: Client-side only, not sent to server
- **Encryption**: None (local storage is not encrypted)

### **Data Lifecycle**
- **Creation**: When order is submitted
- **Access**: When checkout form is displayed
- **Expiration**: After 365 days
- **Deletion**: Manual clear or automatic expiration

### **User Control**
- Users can edit prepopulated data
- Users can clear all data manually
- Data is not shared between devices
- No server-side storage of customer data

## 🚀 Deployment

### **Files Modified**
- `bot/web_app/script.js` - Main implementation
- `tests/unit/test_customer_data.py` - Unit tests

### **Dependencies**
- No external dependencies
- Uses existing localStorage infrastructure
- Integrates with existing form handling

### **Backward Compatibility**
- Graceful handling of missing data
- Legacy data format migration
- No breaking changes to existing functionality

## 📊 Monitoring

### **Data Metrics**
- Customer data age tracking
- Expiration status monitoring
- Storage size monitoring
- Error rate tracking

### **User Experience**
- Form completion time reduction
- Repeat order conversion rate
- User satisfaction metrics

## 🔮 Future Enhancements

### **Potential Improvements**
- Server-side data synchronization
- Cross-device data sharing
- Enhanced data validation
- User preferences storage
- Analytics integration

### **Advanced Features**
- Address book functionality
- Multiple address support
- Payment method persistence
- Order history integration

## 📝 Changelog

### **v1.0.0** (Current)
- ✅ Initial implementation
- ✅ Basic data persistence
- ✅ Form auto-population
- ✅ Expiration handling
- ✅ Cache integration
- ✅ Unit test coverage
- ✅ Debug functions
- ✅ Documentation

---

**Note**: This feature is designed to improve user experience while respecting privacy. All data is stored locally and can be cleared by users at any time.
