Method Endpoint Purpose Access
POST /api/auth/register Register a user Public
POST /api/auth/login Authenticate a user Public
POST /api/auth/logout Log out Logged-in user
GET /api/profile View profile Logged-in user
PATCH /api/profile Update profile Logged-in user
GET /api/rooms List rooms Public or logged-in
GET /api/rooms/<id> View room details Public or logged-in
GET /api/availability Check room availability Public or logged-in
POST /api/bookings Create a booking Logged-in user
GET /api/bookings View current user's bookings Logged-in user
GET /api/bookings/<id> View booking details Booking owner or admin
POST /api/checkouts Process checkout request Authorized user
POST /api/feedback Submit feedback Logged-in user
Admins Route
GET /api/admin/bookings Manage or view bookings Admin only
GET /api/admin/users View users Admin only
GET /api/admin/room view Room current status
GET /api/admin/room/<id> view the detail booking room
Room managenent
Route Function
GET /admin/rooms Display the room management page
GET /api/admin/rooms Retrieve room records
POST /api/admin/rooms Add a room
PUT /api/admin/rooms/<id> Update a room
DELETE /api/admin/rooms/<id> Delete a room, subject to booking restrictions
Booking management
/api/admin/bookings GET Retrieve and filter bookings
/api/admin/bookings/<id> GET View one booking
/api/admin/bookings/<id>/confirm POST Confirm a reservation
/api/admin/bookings/<id>/cancel POST Cancel a reservation
/api/admin/bookings/<id>/checkin POST Record guest arrival
/api/admin/bookings/<id>/checkout POST Record guest departure
