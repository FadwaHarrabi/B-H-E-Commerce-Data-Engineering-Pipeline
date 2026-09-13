variable "postgresql_host"{
    type=string
    default="127.0.0.1"
}
variable "postgresql_port"{
    type=number
    default=5439
}
variable "postgresql_user"{
    type=string
    default="postgres"
}
variable "postgresql_password"{
    type=string
    default="admin"
}
variable "postgresql_database"{
    type=string
    default="bhphotovideo"
}