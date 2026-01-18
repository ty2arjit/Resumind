const mongoose = require('mongoose');

const mongoose_url = process.env.MongoDB_URI;

mongoose.connect(mongoose_url)
.then(() => {
  console.log("MongoDB connected");
}).catch((err) => {
  console.log("MongoDB connection error");
});
