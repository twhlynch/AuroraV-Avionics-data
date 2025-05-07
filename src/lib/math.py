import math


#MARK: Quaternion
class Quaternion:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __str__(self) -> str:
        x, y, z, w = self.x, self.y, self.z, self.w
        return f"({x=},{y=},{z=},{w=})"

    def __array__(self) -> list:
        return [self.x, self.y, self.z, self.w]

    def as_array(self) -> list:
        return self.__array__()

    def __iter__(self):
        for val in self.__array__():
            yield val

    def __getitem__(self, key: int) -> float:
        if key >= len(self):
            raise KeyError
        return self.__array__()[key]

    def __len__(self) -> int:
        return len(self.__array__())

    def normalise(self) -> 'Quaternion':
        """
        Normalises a quaternion.

        Returns: 
            A normalised version of the quaternion.
        """

        p = self
        length = math.sqrt((p.w * p.w) + (p.x * p.x) + (p.y * p.y) + (p.z * p.z))

        if length == 0.0:
            p.x = p.y = p.z = 0
            p.w = 1.0

        else:
            factor = 1.0 / length
            p.x *= factor
            p.y *= factor
            p.z *= factor
            p.w *= factor

        return p

    def multiply(self, other: 'Quaternion') -> 'Quaternion':
        """
        Multiplies two quaternions.

        Args:
            other: The other quaternion.
        Returns:
            A resulting quaternion from the multiplication.
        """

        p = self
        t = other

        result = Quaternion()
        result.x = (p.w * t.x) + (p.x * t.w) + (p.y * t.z) + (-p.z * t.y)
        result.y = (p.w * t.y) + (-p.x * t.z) + (p.y * t.w) + (p.z * t.x)
        result.z = (p.w * t.z) + (p.x * t.y) + (-p.y * t.x) + (p.z * t.w)
        result.w = (p.w * t.w) + (-p.x * t.x) + (-p.y * t.y) + (-p.z * t.z)

        return result

    def apply(self, vector: 'Vector3') -> 'Vector3':
        """
        Applies the quaternion rotation to a 3D vector.

        Args:
            vector: The vector to rotate.
        Returns:
            The rotated vector.
        """
        qx = self.x
        qy = self.y
        qz = self.z
        qw = self.w

        vx = vector.x
        vy = vector.y
        vz = vector.z

        tx = 2 * (qy * vz - qz * vy)
        ty = 2 * (qz * vx - qx * vz)
        tz = 2 * (qx * vy - qy * vx)

        return Vector3(
            vx + qw * tx + qy * tz - qz * ty,
            vy + qw * ty + qz * tx - qx * tz,
            vz + qw * tz + qx * ty - qy * tx
        )

    def with_half_euler(g_roll: float, g_pitch: float, g_yaw: float) -> 'Quaternion':
        """
        Initializes a quaternion from half Euler angles.

        Args:
            g_roll: Roll angle in degrees.
            g_pitch: Pitch angle in degrees.
            g_yaw: Yaw angle in degrees.
        Returns:
            The initialized quaternion.
        """

        # Half the degree and convert it to radians
        x = (g_roll / 2.0) * math.pi / 180.0
        y = (g_pitch / 2.0) * math.pi / 180.0
        z = (g_yaw / 2.0) * math.pi / 180.0

        s_x = math.sin(x)
        c_x = math.cos(x)
        s_y = math.sin(y)
        c_y = math.cos(y)
        s_z = math.sin(z)
        c_z = math.cos(z)

        result = Quaternion()
        result.x = s_x * c_y * c_z - c_x * s_y * s_z
        result.y = c_x * s_y * c_z + s_x * c_y * s_z
        result.z = c_x * c_y * s_z - s_x * s_y * c_z
        result.w = c_x * c_y * c_z + s_x * s_y * s_z

        return result

    def with_array(array: list) -> 'Quaternion':
        """
        Initializes a quaternion from an array.

        Args:
            array: array of 4 floats
        Returns:
            The initialized quaternion.
        """

        return Quaternion(
            array[0],
            array[1],
            array[2],
            array[3]
        )

    def as_euler(self, degrees=False) -> 'Vector3':
        """
        Converts the quaternion to a Euler Vector.

        Returns:
            A Vector3 containing the Euler angles in radians.
        """
        x, y, z, w = self.x, self.y, self.z, self.w

        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        if degrees:
            ratio = 180 / math.pi
            roll *= ratio
            pitch *= ratio
            yaw *= ratio

        return Vector3(roll, pitch, yaw)


#MARK: Vector3
class Vector3():
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        x, y, z = self.x, self.y, self.z
        return f"({x=},{y=},{z=})"

    def __array__(self) -> list:
        return [self.x, self.y, self.z]

    def as_array(self) -> list:
        return self.__array__()

    def __iter__(self):
        for x in self.__array__():
            yield x

    def __getitem__(self, key: int) -> float:
        if key >= len(self):
            raise KeyError
        return self.__array__()[key]

    def __len__(self) -> int:
        return len(self.__array__())

    def with_array(array: list) -> 'Vector3':
        """
        Initializes a vector from an array.

        Args:
            array: array of 3 floats
        Returns:
            The initialized vector.
        """

        return Vector3(
            array[0],
            array[1],
            array[2]
        )